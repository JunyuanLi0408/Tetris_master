def getErodedPieceCellsMetric(block_pos, newboard, block, block_dir):
    # 获取可消行数*方块可消格数
    erodedRow = erodedShape = 0
    erodedRow_lst = []
    for row in range(len(newboard)):
        if 0 not in newboard[row]:
            erodedRow += 1
            erodedRow_lst.append(i)

    # 获取方块所有格子的位置（辅助功能）
    def getAllGrid(block_pos, block, block_dir):
        block_dir = (block_dir + 2) % 4
        # blocks.png与Block.py里的offsetTable一一对应（从左到右分别代表各个type0到3行），这里设定的board的行是越往下编号越大，所以blocks.png与Block.py的一一对应会变成2301
        curr_shape = Block.offsetTable[block][block_dir]
        return [(block_pos[0] - grid[0], block_pos[1] + grid[1]) for grid in curr_shape]
        # offsetTable里所有direction的行（比如(-1,0)的-1）应该要正负号相反，因为本来Block.py offsetTable的设定是行越往下编号越小，而这里设定的board相反

    all_grid = getAllGrid(block_pos, block, block_dir)
    for grid in all_grid:
        if grid[0] in erodedRow_lst:
            erodedShape += 1
    return erodedRow * erodedShape
