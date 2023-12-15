import numpy as np

def getNext_n_Blocks(n,matchdata): # 返回List[int]，为之后的n个块(包括自己正在放的这个块)，注意一个回合是两个块，还要区分先后手
    pass

def method2(origin_list):  # 取代deepcopy
    l = np.array(origin_list).tolist()
    assert type(l) == type(origin_list)
    return l

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


def copy_board(board, is_first):  # 获取己方或对方棋盘的深拷贝对象
    if is_first:
        return method2(board)
    else:
        board2 = method2(board)
        for i in board2:
            i.reverse()
        board2.reverse()
        return method2(board2)

class Decision_tree:
    def __init__(self, blockpos, board, depth, parent=None):  # 树根为一个局面，储存有以下信息
        self.currentblock = blocklst[depth - 1]
        self.nextblock = blocklst[depth]
        self.blockpos = blockpos  # 局面的第一部分：当前方块 即将 放置的位置(如果是对方放块，这就是 对方视角 中的位置)
        self.board = board  # 局面的第二部分：当前还没放置currentblock的棋盘(如果是对方放块，这就是 对方视角 中的棋盘)
        self.depth = depth
        self.is_first = False if (depth % 2) else True  # 当前层是max还是min层，max为True
        self.whoseblock = not self.is_first  # currentblock的归属，min层是我方(nextblock是对方放置，因此是min层)
        self.alphabeta = None
        self.parent = parent
        self.children = []  # 储存进行一步操作之后的子树

    def evaluate(self,matchdata):  # 返回我方视角下的局面估值
        if self.whoseblock:  # 如果局面中的块是我方的，正常估值
            pass
        else:  # 如果局面中的块是对方的，注意估值的时候要把棋盘转过来(注意self.board是对方视角的棋盘)
            # 有可能对方的块影响不到我们(在和平区)，可以简化估值；如果能影响到就更复杂
            pass

    def update_board(self, matchdata):  # 把当前局面结算，返回一个新的棋盘List[List[int]]，是各自视角中的棋盘
        temp_board = matchdata.putBlock(self.currentblock, self.blockpos, self.board)
        new_board = matchdata.removeLines(temp_board)
        return new_board[0]

    def minmaxsearch(self, matchdata, max_depth):
        # 返回当前局面的估值
        if self.depth == max_depth:
            return self.evaluate()  # 搜索深度达到上限直接返回估值

        else:
            newboard = self.update_board(matchdata)  # 更新得到各自视角下的棋盘
            nextboard = copy_board(newboard, False)  # 子树会轮到另一方落块，切换board视角(不一定要深拷贝)
            all_pos = matchdata.getAllValidAction(self.nextblock, nextboard)  # 另一方落块所有可能的操作
            value_lst = {}  # 字典储存每个子节点的估值
            for i in range(len(all_pos)):
                child_i = Decision_tree(all_pos[i], nextboard, self.depth + 1, self)  # 创建子树
                self.children.append(child_i)
                value_i = child_i.minmaxsearch(matchdata, max_depth)
                value_lst[child_i] = value_i  # 递归取得子树的估值，加入字典
                if self.parent:  # 开始alpha-beta剪枝
                    if (self.parent.alphabeta is not None) \
                            and ((self.is_first and value_i >= self.parent.alphabeta) or \
                                 (not self.is_first and value_i <= self.parent.alphabeta)):
                        break
            value = max(value_lst.values()) if self.is_first else min(value_lst.values()) # 得到该节点的估值
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
        max_depth=2
        blocklst=getNext_n_Blocks(max_depth+1,matchdata)
        nowboard = matchdata.getBoard()
        nowblock = blocklst[0]
        validpos = matchdata.getAllValidAction(nowblock, nowboard)
        values={}
        for i in range(len(validpos)):
            case_i=Decision_tree(validpos[i],nowboard,1)
            values[case_i]=case_i.minmaxsearch(matchdata,max_depth)
        value_lst=sorted(values.items(),key = lambda x:x[1],reverse = True)
        return value_lst[0][0]





