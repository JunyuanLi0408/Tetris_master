def getNext_n_Blocks(n, is_first, matchdata):  # 返回List[int]，至少为之后的n个块(包括自己正在放的这个块)
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
    return lst


def buried_holes(newboard):  # 注：newboard 为已经配置好新方块的棋盘
    # 思路：下边界已经固定，只需要从上往下（0-n）遍历每一列（y），如遇到方块（1），该方块过后的所有（0）都为洞
    holes = 0
    for x in range(len(newboard[0])):  # y遍历
        colHoles = None  # 如果遇到当前列最顶端的1，colHoles 就不为None
        for y in range(len(newboard)):  # y遍历 （从上放往下，遍历当前列）
            if colHoles == None and newboard[y][x] != 0:  # 尚未遍历到该列最顶端的1，当前值又为1
                colHoles = 0  # 遇到了该列的上界（当前列最顶端的）

            if colHoles != None and newboard[y][x] == 0:  # 如果已经上边界已经存在，当前值又为0
                colHoles += 1  # 洞口+1
        if colHoles is not None:
            holes += colHoles
    return holes


def getLandingHeight(block_pos):  # 输入棋盘和方块位置，返回下落高度
    return 15 - block_pos[0]


def getErodedPieceCellsMetric(board, cells):  # board is board before placing current piece
    lines = 0
    usefulblocks = 0
    for i in board:
        if 0 not in i:
            lines += 1
            for j in cells:
                if j[0] == i:
                    usefulblocks += 1

    return lines * usefulblocks


def BoardRowTransition(newboard):  # 注：newboard 为已经配置好新方块的棋盘
    transitions = 0
    for y in range(len(newboard) - 1, 0, -1):  # y遍历
        for x in range(len(newboard[0]) - 1):  # x遍历
            if newboard[y][x] != newboard[y][x + 1]:
                transitions += 1
    return transitions


def BoardColTransition(newboard):  # 注：newboard 为已经配置好新方块的棋盘
    transitions = 0
    for x in range(len(newboard[0])):
        for y in range(len(newboard) - 1, 0, -1):
            if newboard[y][x] != newboard[y - 1][x]:
                transitions += 1
    return transitions


def getBoardWells(newboard):
    # 返回井值
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

def action_sort(element):
    decision_tree = element[0]
    score = element[1]
    dist = decision_tree.blockpos[0]
    return (-score , -dist)

class Decision_tree:
    def __init__(self, blockpos, board, blocklst, depth, parent=None):  # 树根为一个局面，储存有以下信息
        self.blocklst = blocklst
        self.currentblock = blocklst[depth - 1]
        self.nextblock = blocklst[depth] if len(blocklst) > 1 else None
        self.blockpos = blockpos  # 局面的第一部分：当前方块 即将 放置的位置(如果是对方放块，这就是 对方视角 中的位置)
        self.board = board  # 局面的第二部分：当前还没放置currentblock的棋盘(如果是对方放块，这就是 对方视角 中的棋盘)
        self.depth = depth
        self.is_first = False if (depth % 2) else True  # 当前层是max还是min层，max为True
        self.whoseblock = not self.is_first  # currentblock的归属，min层是我方(nextblock是对方放置，因此是min层)
        self.alphabeta = None
        self.parent = parent

    def evaluate(self, matchdata):  # 返回我方视角下的局面估值
        my_board = copy_board(self.board, True)
        newboard = matchdata.putBlock(self.currentblock, self.blockpos,
                                      my_board)  # before delete lines,placed current block
        newboard2 = matchdata.removeLines(newboard)  # delete lines
        if self.whoseblock:  # 如果局面中的块是我方的，正常估值
            newboard3 = newboard2[0][:15]  # board after deleted lines, and placed current block

            now_cells = matchdata.getCells(self.currentblock, self.blockpos)  # for getErodedPieceCellsMetric
            landing_height = getLandingHeight(self.blockpos)
            buried_holes2 = buried_holes(newboard3)
            row_trans = BoardRowTransition(newboard3)
            wells = getBoardWells(newboard3)
            col_trans = BoardColTransition(newboard3)
            eroded = getErodedPieceCellsMetric(newboard, now_cells)

            j = 1
            if landing_height <= 4:
                i = 0
                j = 2
            elif 5 <= landing_height <= 9:
                i = 2
            else:
                i = 6
            return -(i * landing_height) - (11 * buried_holes2) - (3 * row_trans) - (5 * wells) - (10 * col_trans) + (
                    eroded * j * 3)

        else:  # 如果局面中的块是对方的，注意估值的时候要把棋盘转过来(注意self.board是对方视角的棋盘)
            newboard3 = (copy_board(newboard2[0], False))[:15]  # board after deleted lines, and placed current block

            buried_holes2 = buried_holes(newboard3)
            row_trans = BoardRowTransition(newboard3)
            wells = getBoardWells(newboard3)
            col_trans = BoardColTransition(newboard3)

            return - (11 * buried_holes2) - (3 * row_trans) - (5 * wells) - (10 * col_trans)

    def update_board(self, matchdata):  # 把当前局面结算，返回一个新的棋盘List[List[int]]，是各自视角中的棋盘
        my_board = method2(self.board)
        temp_board = matchdata.putBlock(self.currentblock, self.blockpos, my_board)
        new_board = matchdata.removeLines(temp_board)
        return new_board[0]

    def minmaxsearch(self, matchdata, max_depth):
        # 返回当前局面的估值
        if self.depth == max_depth:
            return self.evaluate(matchdata)  # 搜索深度达到上限直接返回估值

        else:
            newboard = self.update_board(matchdata)  # 更新得到各自视角下的棋盘
            nextboard = copy_board(newboard, False)  # 子树会轮到另一方落块，切换board视角(不一定要深拷贝)
            all_pos = matchdata.getAllValidAction(self.nextblock, nextboard)  # 另一方落块所有可能的操作
            value_lst = {}  # 字典储存每个子节点的估值

            if len(all_pos) > 0:
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
            else:
                value = self.evaluate(matchdata)
            if self.parent:  # 更新alpha-beta值
                if self.parent.alphabeta is None:
                    self.parent.alphabeta = value
                elif (self.is_first and value < self.parent.alphabeta) \
                        or (not self.is_first and value > self.parent.alphabeta):
                    self.parent.alphabeta = value
            return value


class Player:
    def __init__(self, isFirst):
        self.isFirst = isFirst

    def output(self, matchdata):
        max_depth = 2 if matchdata.getCurrentRound() < 279 else 1  # 搜索层数
        blocklst = getNext_n_Blocks(max_depth + 2, self.isFirst, matchdata)
        nowboard = matchdata.getBoard()
        nowblock = blocklst[0]
        validpos = matchdata.getAllValidAction(nowblock, nowboard)
        values = {}
        this_case = Decision_tree(None, nowboard, blocklst, 0)

        for i in range(len(validpos)):
            case_i = Decision_tree(validpos[i], nowboard, blocklst, 1, this_case)

            values[case_i] = case_i.minmaxsearch(matchdata, max_depth)

        value_lst = sorted(values.items(), key=action_sort)
        return value_lst[0][0].blockpos
