# 以下是与估值函数相关的辅助函数，各个量的定义参考了PD算法
def macroheight(newboard):  # 返回某方棋盘内最高方块的高度
    height = 0  # 初始为0，全局最高方块的高度
    notfound = True  # 尚未找到最高，从板块的最高处开始搜索index 0,1,2....,直到找到'1'（方块）改为False
    for y in range(len(newboard)):  # 从上往下查找
        for x in range(len(newboard[0])):  # 从左到右查找
            if newboard[y][x] == 1:  # 找到‘1’ 方块
                height = 15 - y  # 改为全局最高方块的高度
                notfound = False  # 找到第一个‘1’
                break  # 找到第一个（最高）就break
        if not notfound:  # 如果当前的行中找到了‘1’
            break  # 结束遍历
    return height  # 返回某方棋盘内最高方块的高度


def buried_holes(newboard):  # 返回某方棋盘内洞的数量
    # 思路：下边界已经固定，只需要从上往下（0-n）遍历每一列（y），如遇到方块（1），该方块过后的所有（0）都为洞
    holes = 0  # 初始洞口数量
    for x in range(len(newboard[0])):  # y遍历
        colHoles = None  # 如果遇到当前列最顶端的1，colHoles 就不为None
        for y in range(len(newboard)):  # y遍历 （从上放往下，遍历当前列）
            if colHoles == None and newboard[y][x] != 0:  # 尚未遍历到该列最顶端的1，当前值又为1
                colHoles = 0  # 遇到了该列的上界（当前列最顶端的）

            if colHoles != None and newboard[y][x] == 0:  # 如果已经上边界已经存在，当前值又为0
                colHoles += 1  # 洞口+1
        if colHoles is not None:  # 当前列最顶端为1（有顶）
            holes += colHoles  # 将当前列的洞口加入总洞口数
    return holes  # 返回某方棋盘内洞的数量


def getLandingHeight(block_pos):  # 输入棋盘和方块位置，返回下落高度
    return 15 - block_pos[0]


def getErodedPieceCellsMetric(board, cells):  # 返回消行数*有用方块数(四个方块中参与消行的数目)
    lines = 0
    usefulblocks = 0
    for i in board:
        if 0 not in i:
            lines += 1
            for j in cells:
                if j[0] == i:
                    usefulblocks += 1

    return lines * usefulblocks


def BoardRowTransition(newboard):  # 返回某方棋盘内的行变换数
    transitions = 0  # 初始变化数量
    for y in range(len(newboard) - 1, 0, -1):  # y遍历
        for x in range(len(newboard[0]) - 1):  # x遍历
            if newboard[y][x] != newboard[y][x + 1]:  # 如果当前方块不等于下一个方块
                transitions += 1  # 变化+1
    return transitions  # 返回某方棋盘内的行变换数


def BoardColTransition(newboard):  # 返回某方棋盘内的列变换数
    transitions = 0  # 初始变化数量
    for x in range(len(newboard[0])):  # x遍历
        for y in range(len(newboard) - 1, 0, -1):  # y遍历
            if newboard[y][x] != newboard[y - 1][x]:  # 如果当前方块不等于下一个方块
                transitions += 1  # 变化+1
    return transitions  # 返回某方棋盘内的列变换数


def getBoardWells(newboard):  # 返回井值
    sum_n = [0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105, 120]
    wells = 0
    sum = 0
    for x in range(len(newboard[0])):
        for y in range(len(newboard)):
            if newboard[y][x] == 0:
                if (x - 1 < 0 or newboard[y][x - 1] == 1) and (
                        x + 1 >= len(newboard[0]) or newboard[y][x + 1] == 1):
                    wells += 1
            else:
                sum += sum_n[wells]
                wells = 0
    return sum


# 第一部分结束，以下是其他辅助函数
def method2(origin_list):  # 取代deepcopy
    return list(map(list, origin_list))


def copy_board(board, is_first):  # 获取己方或对方棋盘的深拷贝对象
    if is_first:
        return method2(board)
    else:
        board2 = method2(board)
        for i in board2:
            i.reverse()
        board2.reverse()
        return board2


def action_sort(element):  # 二键值排序的辅助函数，优先按估值降序排序，其次按方块高度降序排序
    decision_tree = element[0]
    score = element[1]
    dist = decision_tree.blockpos[0]
    return (-score, -dist)


def getNext_n_Blocks(n, is_first, matchdata):  # 返回之后的n个块(包括自己正在放的这个块)(List[int])
    rounds = n // 2  # 考虑之后这么多回合数
    current_round = matchdata.getCurrentRound()
    lst = []
    if is_first is False:  # 如果是后手就要先加入这个回合的块
        lst.append(matchdata.getBlock(current_round, False))
        current_round += 1
    for i in range(rounds):
        if current_round > 280:
            break
        lst.append(matchdata.getBlock(current_round, True))
        lst.append(matchdata.getBlock(current_round, False))
        current_round += 1
    return lst  # 返回之后的n个块


# 第二部分结束，以下是决策树(节点)类
class Decision_tree:
    def __init__(self, blockpos, board, blocklst, depth, parent=None):  # 树根为一个局面，储存有以下信息
        self.blocklst = blocklst  # 之后的若干个块
        self.currentblock = blocklst[depth - 1]  # 当前要放置的块
        self.nextblock = blocklst[depth] if len(blocklst) > 1 else None  # 下一个要放置的块
        self.blockpos = blockpos  # 局面的第一部分：当前方块即将放置的位置(如果是对方放块，这是对方视角中的位置)
        self.board = board  # 局面的第二部分：还未放置当前方块的棋盘(如果是对方放块，这是对方视角中的棋盘)
        self.depth = depth  # 当前深度
        self.is_first = False if (depth % 2) else True  # 当前层是max还是min层，max为True
        self.whoseblock = not self.is_first  # 当前块的归属，min层是我方(下一个块是对方放置，因此是min层)
        self.alphabeta = None
        self.parent = parent

    def evaluate(self, matchdata):  # 返回我方视角下的局面估值
        my_board = copy_board(self.board, True)
        newboard = matchdata.putBlock(self.currentblock, self.blockpos, my_board)  # 放置当前块
        newboard2 = matchdata.removeLines(newboard)  # 消行结算
        if self.whoseblock:  # 如果局面中的块是我方的，直接估值
            newboard3 = newboard2[0][:15]  # 取我方棋盘
            now_cells = matchdata.getCells(self.currentblock, self.blockpos)
            # 返回下落高度、空洞数、行列变换数、井以及消行数
            landing_height = getLandingHeight(self.blockpos)
            buried_holes2 = buried_holes(newboard3)
            row_trans = BoardRowTransition(newboard3)
            wells = getBoardWells(newboard3)
            col_trans = BoardColTransition(newboard3)
            eroded = getErodedPieceCellsMetric(newboard, now_cells)

            # 根据下落高度不同调节下落高度以及消行数在估值函数中的权重
            j = 1
            if landing_height <= 4:
                i = 0
                j = 2
            elif 5 <= landing_height <= 9:
                i = 2
            else:
                i = 4
            return -(i * landing_height) - (11 * buried_holes2) - (3 * row_trans) - (5 * wells) - (10 * col_trans) + (
                    eroded * j * 3)


        else:  # 如果局面中的块是对方的，仍然只考虑我方的15行棋盘，于是估值的时候要把棋盘转过来(self.board是对方视角的棋盘)
            newboard3 = (copy_board(newboard2[0], False))[:15]
            buried_holes2 = buried_holes(newboard3)
            row_trans = BoardRowTransition(newboard3)
            wells = getBoardWells(newboard3)
            col_trans = BoardColTransition(newboard3)
            height = macroheight(newboard3)
            if height <= 4:
                i = 0
            elif 5 <= height <= 9:
                i = 2
            else:
                i = 8
            return - (11 * buried_holes2) - (3 * row_trans) - (5 * wells) - (10 * col_trans) - (i * height)

    def update_board(self, matchdata):  # 把当前局面结算，返回一个新的棋盘List[List[int]]，是各自视角中的棋盘
        my_board = method2(self.board)
        temp_board = matchdata.putBlock(self.currentblock, self.blockpos, my_board)
        new_board = matchdata.removeLines(temp_board)
        return new_board[0]

    def minmaxsearch(self, matchdata, max_depth):
        # 用min_max_search返回当前局面的估值
        if self.depth == max_depth:
            return self.evaluate(matchdata)  # 搜索深度达到上限直接返回估值

        else:
            newboard = self.update_board(matchdata)  # 更新得到各自视角下的棋盘
            nextboard = copy_board(newboard, False)  # 子节点会轮到另一方落块，得到另一方视角下的棋盘
            all_pos = matchdata.getAllValidAction(self.nextblock, nextboard)  # 另一方落块所有可能的操作
            value_lst = {}  # 字典储存每个子节点的估值

            if len(all_pos) > 0:  # 递归考虑每一种所有可能操作的估值
                for i in range(len(all_pos)):
                    child_i = Decision_tree(all_pos[i], nextboard, self.blocklst, self.depth + 1, self)  # 创建子树
                    value_i = child_i.minmaxsearch(matchdata, max_depth)
                    value_lst[child_i] = value_i  # 递归取得子树的估值，加入字典
                    if self.parent:  # 开始alpha-beta剪枝
                        if (self.parent.alphabeta is not None) \
                                and ((self.is_first and value_i >= self.parent.alphabeta) or \
                                     (not self.is_first and value_i <= self.parent.alphabeta)):
                            break
                value = max(value_lst.values()) if self.is_first else min(value_lst.values())  # 得到该节点的估值
            else:  # 如果是死局就直接返回估值
                value = self.evaluate(matchdata)
            if self.parent:  # 更新alpha-beta值
                if self.parent.alphabeta is None:
                    self.parent.alphabeta = value
                elif (self.is_first and value < self.parent.alphabeta) \
                        or (not self.is_first and value > self.parent.alphabeta):
                    self.parent.alphabeta = value
            return value


# 第三部分结束，以下是Player类
class Player:
    def __init__(self, isFirst):
        self.isFirst = isFirst

    def output(self, matchdata):
        max_depth = 2 if matchdata.getCurrentRound() < 279 else 1  # 设定搜索层数，一般为两层
        blocklst = getNext_n_Blocks(max_depth + 2, self.isFirst, matchdata)  # 取得接下来几个回合的方块
        nowboard = matchdata.getBoard()
        nowblock = blocklst[0]
        validpos = matchdata.getAllValidAction(nowblock, nowboard)
        values = {}
        this_case = Decision_tree(None, nowboard, blocklst, 0)  # 初始化一个局面作为树根

        for i in range(len(validpos)):
            case_i = Decision_tree(validpos[i], nowboard, blocklst, 1, this_case)  # 创建树根的子节点
            values[case_i] = case_i.minmaxsearch(matchdata, max_depth)  # 搜索得到该节点的估值

        value_lst = sorted(values.items(), key=action_sort)  # 排序得到最优决策
        return value_lst[0][0].blockpos
