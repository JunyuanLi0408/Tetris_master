import copy

def getNext_n_Blocks(n, is_first,matchdata):  # 返回List[int]，至少为之后的n个块(包括自己正在放的这个块)
    rounds=n//2 # 考虑之后这么多回合数
    current_round=matchdata.getCurrentRound()
    lst=[]
    if is_first is False: # 如果是后手就要先加入这个回合的块
        lst.append(matchdata.getBlock(current_round, False))
        current_round+=1
    for i in range(rounds):
        lst.append(matchdata.getBlock(current_round, True))
        lst.append(matchdata.getBlock(current_round, False))
        current_round += 1
    return lst

def getLandingHeight(block_pos):
    # 输入棋盘和方块位置，返回下落高度
    return 15 - block_pos[0]

def getErodedPieceCellsMetric(board,cells):
            lines = 0
            usefulblocks = 0
            for i in board:
                if 0 not in i:
                    lines += 1
                    for j in cells:
                        if j[0]==i:
                            usefulblocks += 1

            return lines*usefulblocks

def evaluate(landing_height, eroded, row_trans, col_trans, buried_holes, wells, combos):
    j=1
    if landing_height<=4:
        i=0
        j=2
    elif 5<=landing_height<=9:
        i=2
    else:
        i=6

    return  -i*landing_height-11*buried_holes-5*wells-10*col_trans+eroded*j*3

class Player:
    def __init__(self, isFirst):
        self.isFirst = isFirst

    def output(self, matchdata):


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

        def find_best_choice(matchdata):
            nowboard = matchdata.getBoard()
            nowblock = matchdata.getCurrentBlock()
            print(nowblock)
            validpos = matchdata.getAllValidAction(nowblock, nowboard)
            values = []
            bestChoice = validpos[0]
            holes = []
            block_lst=getNext_n_Blocks(2,self.isFirst,matchdata)
            print(block_lst)

            for i in range(len(validpos)):
                # 遍历每种操作，将估值加入表中
                temp_nowboard = copy.deepcopy(nowboard)
                tempboard = matchdata.putBlock(nowblock, validpos[i], temp_nowboard)
                newboard = matchdata.removeLines(tempboard)
                myboard = newboard[0][:15]
                l_h = getLandingHeight(validpos[i])
                brt = BoardRowTransition(myboard)
                bct = BoardColTransition(myboard)
                bh = buried_holes(myboard)
                bw = getBoardWells(myboard)
                nowcells = matchdata.getCells(nowblock,validpos[i])
                eroded = getErodedPieceCellsMetric(tempboard[:15],nowcells)
                values.append(evaluate(l_h, eroded, brt, bct, bh, bw, 0))
                holes.append(bh)

            bestScore = -999999
            h = None
            for i in range(len(values)):
                # 输出最高分和对应操作
                if values[i] > bestScore:
                    bestScore = values[i]
                    bestChoice = validpos[i]
                    h = i
                elif values[i]==bestScore:
                    if holes[i] > holes[h]:
                        bestScore = values[i]
                        bestChoice = validpos[i]
                        h = i
            return bestChoice

        bestChoice = find_best_choice(matchdata)
        return bestChoice