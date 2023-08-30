#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
import pprint
import copy

class Block_Controller(object):

    # init parameter
    board_backboard = 0
    board_data_width = 0
    board_data_height = 0
    ShapeNone_index = 0
    CurrentShape_class = 0
    NextShape_class = 0
    HoldShape_class = 0
    NNextShape_class = 0

    hold_flg = 0
    hold_flg2 = 0
    hold_flg3 = 0
    hold_first_error_avoid_flg = 0
    pre_isolatedblocks = 0

    # GetNextMove is main function.
    # input
    #    nextMove : nextMove structure which is empty.
    #    GameStatus : block/field/judge/debug information. 
    #                 in detail see the internal GameStatus data.
    # output
    #    nextMove : nextMove structure which includes next shape position and the other.
    def GetNextMove(self, nextMove, GameStatus):

        t1 = datetime.now()

        # print GameStatus
        print("=================================================>")
        pprint.pprint(GameStatus, width = 61, compact = True)

        # get data from GameStatus
        # current shape info
        CurrentShapeDirectionRange = GameStatus["block_info"]["currentShape"]["direction_range"]
        self.CurrentShape_class = GameStatus["block_info"]["currentShape"]["class"]
        # next shape info
        NextShapeDirectionRange = GameStatus["block_info"]["nextShape"]["direction_range"]
        self.NextShape_class = GameStatus["block_info"]["nextShape"]["class"]
        # hold shape info
        HoldShapeDirectionRange = GameStatus["block_info"]["holdShape"]["direction_range"]
        self.HoldShape_class = GameStatus["block_info"]["holdShape"]["class"]
        # Next Next shape info
        NNextShapeDirectionRange = GameStatus["block_info"]["nextShapeList"]["element0"]["direction_range"]
        self.NNextShape_class = GameStatus["block_info"]["nextShapeList"]["element0"]["class"]
        # current board info
        self.board_backboard = GameStatus["field_info"]["backboard"]
        # default board definition
        self.board_data_width = GameStatus["field_info"]["width"]
        self.board_data_height = GameStatus["field_info"]["height"]
        self.ShapeNone_index = GameStatus["debug_info"]["shape_info"]["shapeNone"]["index"]

        # search best nextMove -->
        #全探索は時間がかかりすぎる、次のブロックとかを計算しようとすると
        strategy = None # 全探索
        LatestEvalValue = -100000

        tmp_isolatedblocks = 0

        if (self.hold_flg == 0) and (self.hold_flg2 == 0):
            for direction1 in NextShapeDirectionRange:
                x1Min, x1Max = self.getSearchXRange(self.NextShape_class, direction1)
                for x1 in range(x1Min, x1Max):
                    board2 = self.getBoard(self.board_backboard, self.NextShape_class, direction1, x1)
                    EvalValue_1, tmp_isolatedblocks = self.calcEvaluationValueSample(board2, self.pre_isolatedblocks, self.CurrentShape_class)
                    for direction0 in CurrentShapeDirectionRange: # 4通りの回転
                        # search with x range
                        x0Min, x0Max = self.getSearchXRange(self.CurrentShape_class, direction0)
                        for x0 in range(x0Min, x0Max): # x軸9個のどこにおけばいいのか
                            # get board data, as if dropdown block
                            board = self.getBoard(board2, self.CurrentShape_class, direction0, x0)
                            # evaluate board
                            EvalValue_2, tmp_isolatedblocks = self.calcEvaluationValueSample(board, self.pre_isolatedblocks, self.CurrentShape_class) # 盤面の評価
                            EvalValue = EvalValue_1 + EvalValue_2
                            if EvalValue > LatestEvalValue:
                                strategy = (direction1, x1, 1, 1, tmp_isolatedblocks)
                                LatestEvalValue = EvalValue
                                self.hold_flg = 1

        # search with current block Shape
        if (self.hold_flg == 0) and (self.hold_flg2 == 0):
            for direction0 in CurrentShapeDirectionRange: # 4通りの回転
                # search with x range
                x0Min, x0Max = self.getSearchXRange(self.CurrentShape_class, direction0)
                for x0 in range(x0Min, x0Max): # x軸9個のどこにおけばいいのか
                    # get board data, as if dropdown block
                    board = self.getBoard(self.board_backboard, self.CurrentShape_class, direction0, x0)
                    # evaluate board
                    EvalValue_1, tmp_isolatedblocks = self.calcEvaluationValueSample(board, self.pre_isolatedblocks, self.CurrentShape_class) # 盤面の評価
                    # holdするか否かの評価は入っていない
                    # update best move
                    for direction1 in NextShapeDirectionRange:
                        x1Min, x1Max = self.getSearchXRange(self.NextShape_class, direction1)
                        for x1 in range(x1Min, x1Max):
                            board2 = self.getBoard(board, self.NextShape_class, direction1, x1)
                            EvalValue_2, tmp_isolatedblocks = self.calcEvaluationValueSample(board2, self.pre_isolatedblocks, self.CurrentShape_class)
                            EvalValue = EvalValue_1 + EvalValue_2
                            if EvalValue > LatestEvalValue:
                                strategy = (direction0, x0, 1, 1, tmp_isolatedblocks) # 一番よかった方向と位置を覚える
                                LatestEvalValue = EvalValue
                                self.hold_flg = 0
                                nextMove["strategy"]["use_hold_function"] = "n"

        # search best nextMove <--

        if (self.hold_flg == 1) and (self.hold_flg2 == 0):
            self.hold_first_error_avoid_flg = 1
            self.hold_flg2 = 1
            nextMove["strategy"]["use_hold_function"] = "y"

        if (self.hold_flg == 1) and (self.hold_flg2 == 1) and (self.hold_first_error_avoid_flg == 0):
            for direction2 in HoldShapeDirectionRange:
                x2Min, x2Max = self.getSearchXRange(self.HoldShape_class, direction2)
                for x2 in range(x2Min, x2Max):
                    board3 = self.getBoard(self.board_backboard, self.HoldShape_class, direction2, x2)
                    EvalValue_1, tmp_isolatedblocks = self.calcEvaluationValueSample(board3, self.pre_isolatedblocks, self.CurrentShape_class)
                    for direction0 in CurrentShapeDirectionRange: # 4通りの回転
                        # search with x range
                        x0Min, x0Max = self.getSearchXRange(self.CurrentShape_class, direction0)
                        for x0 in range(x0Min, x0Max): # x軸9個のどこにおけばいいのか
                            # get board data, as if dropdown block
                            board = self.getBoard(board3, self.CurrentShape_class, direction0, x0)
                            # evaluate board
                            EvalValue_2, tmp_isolatedblocks = self.calcEvaluationValueSample(board, self.pre_isolatedblocks, self.CurrentShape_class) # 盤面の評価
                            EvalValue = EvalValue_1 + EvalValue_2
                            if EvalValue > LatestEvalValue:
                                strategy = (direction2, x2, 1, 1, tmp_isolatedblocks)
                                LatestEvalValue = EvalValue
                                self.hold_flg3 = 1

        if (self.hold_flg == 1) and (self.hold_flg2 == 1) and (self.hold_first_error_avoid_flg == 0):
            for direction2 in HoldShapeDirectionRange:
                x2Min, x2Max = self.getSearchXRange(self.HoldShape_class, direction2)
                for x2 in range(x2Min, x2Max):
                    board3 = self.getBoard(self.board_backboard, self.HoldShape_class, direction2, x2)
                    EvalValue_1, tmp_isolatedblocks = self.calcEvaluationValueSample(board3, self.pre_isolatedblocks, self.CurrentShape_class)
                    for direction1 in NextShapeDirectionRange:
                        x1Min, x1Max = self.getSearchXRange(self.NextShape_class, direction1)
                        for x1 in range(x1Min, x1Max):
                            board2 = self.getBoard(board3, self.NextShape_class, direction1, x1)
                            EvalValue_2, tmp_isolatedblocks = self.calcEvaluationValueSample(board2, self.pre_isolatedblocks, self.CurrentShape_class)
                            EvalValue = EvalValue_1 + EvalValue_2
                            if EvalValue > LatestEvalValue:
                                strategy = (direction2, x2, 1, 1, tmp_isolatedblocks) # 一番よかった方向と位置を覚える
                                LatestEvalValue = EvalValue
                                self.hold_flg3 = 1

        if (self.hold_flg == 1) and (self.hold_flg2 == 1) and (self.hold_first_error_avoid_flg == 0):
            for direction0 in CurrentShapeDirectionRange: # 4通りの回転
                # search with x range
                x0Min, x0Max = self.getSearchXRange(self.CurrentShape_class, direction0)
                for x0 in range(x0Min, x0Max): # x軸9個のどこにおけばいいのか
                    # get board data, as if dropdown block
                    board = self.getBoard(self.board_backboard, self.CurrentShape_class, direction0, x0)
                    # evaluate board
                    EvalValue_1, tmp_isolatedblocks = self.calcEvaluationValueSample(board, self.pre_isolatedblocks, self.CurrentShape_class) # 盤面の評価
                    for direction1 in NextShapeDirectionRange:
                        x1Min, x1Max = self.getSearchXRange(self.NextShape_class, direction1)
                        for x1 in range(x1Min, x1Max):
                            board2 = self.getBoard(board, self.NextShape_class, direction1, x1)
                            EvalValue_2, tmp_isolatedblocks = self.calcEvaluationValueSample(board2, self.pre_isolatedblocks, self.CurrentShape_class)
                            EvalValue = EvalValue_1 + EvalValue_2
                            if EvalValue > LatestEvalValue:
                                strategy = (direction0, x0, 1, 1, tmp_isolatedblocks) # 一番よかった方向と位置を覚える
                                LatestEvalValue = EvalValue
                                self.hold_flg3 = 0
                                nextMove["strategy"]["use_hold_function"] = "n"
        
        if (self.hold_flg == 1) and (self.hold_flg2 == 1) and (self.hold_first_error_avoid_flg == 0):
            for direction0 in CurrentShapeDirectionRange: # 4通りの回転
                # search with x range
                x0Min, x0Max = self.getSearchXRange(self.CurrentShape_class, direction0)
                for x0 in range(x0Min, x0Max): # x軸9個のどこにおけばいいのか
                    # get board data, as if dropdown block
                    board = self.getBoard(self.board_backboard, self.CurrentShape_class, direction0, x0)
                    # evaluate board
                    EvalValue_1, tmp_isolatedblocks = self.calcEvaluationValueSample(board, self.pre_isolatedblocks, self.CurrentShape_class) # 盤面の評価
                    for direction2 in HoldShapeDirectionRange:
                        x2Min, x2Max = self.getSearchXRange(self.HoldShape_class, direction2)
                        for x2 in range(x2Min, x2Max):
                            board3 = self.getBoard(board, self.HoldShape_class, direction2, x2)
                            EvalValue_2, tmp_isolatedblocks = self.calcEvaluationValueSample(board3, self.pre_isolatedblocks, self.CurrentShape_class)
                            EvalValue = EvalValue_1 + EvalValue_2
                            if EvalValue > LatestEvalValue:
                                strategy = (direction0, x0, 1, 1, tmp_isolatedblocks) # 一番よかった方向と位置を覚える
                                LatestEvalValue = EvalValue
                                self.hold_flg3 = 0
                                nextMove["strategy"]["use_hold_function"] = "n"

        if (self.hold_flg3 == 1):
            nextMove["strategy"]["use_hold_function"] = "y"

        print("===", datetime.now() - t1)
        nextMove["strategy"]["direction"] = strategy[0]
        nextMove["strategy"]["x"] = strategy[1]
        nextMove["strategy"]["y_operation"] = strategy[2]
        nextMove["strategy"]["y_moveblocknum"] = strategy[3]
        self.pre_isolatedblocks = strategy[4]
        print(nextMove)
        print(self.hold_flg, self.hold_flg2, self.hold_flg3, self.hold_first_error_avoid_flg, self.pre_isolatedblocks, self.CurrentShape_class.shape)
        print("###### SAMPLE CODE ######")

        self.hold_flg3 = 0
        self.hold_first_error_avoid_flg = 0

        return nextMove

    def getSearchXRange(self, Shape_class, direction):
        #
        # get x range from shape direction.
        #
        minX, maxX, _, _ = Shape_class.getBoundingOffsets(direction) # get shape x offsets[minX,maxX] as relative value.
        xMin = -1 * minX
        xMax = self.board_data_width - maxX
        return xMin, xMax

    def getShapeCoordArray(self, Shape_class, direction, x, y):
        #
        # get coordinate array by given shape.
        #
        coordArray = Shape_class.getCoords(direction, x, y) # get array from shape direction, x, y.
        return coordArray

    def getBoard(self, board_backboard, Shape_class, direction, x):
        # 
        # get new board.
        #
        # copy backboard data to make new board.
        # if not, original backboard data will be updated later.
        board = copy.deepcopy(board_backboard)
        _board = self.dropDown(board, Shape_class, direction, x)
        return _board

    def dropDown(self, board, Shape_class, direction, x):
        # 
        # internal function of getBoard.
        # -- drop down the shape on the board.
        # 
        dy = self.board_data_height - 1
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        # update dy
        for _x, _y in coordArray:
            _yy = 0
            while _yy + _y < self.board_data_height and (_yy + _y < 0 or board[(_y + _yy) * self.board_data_width + _x] == self.ShapeNone_index):
                _yy += 1
            _yy -= 1
            if _yy < dy:
                dy = _yy
        # get new board
        _board = self.dropDownWithDy(board, Shape_class, direction, x, dy)
        return _board

    def dropDownWithDy(self, board, Shape_class, direction, x, dy):
        #
        # internal function of dropDown.
        #
        _board = board
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        for _x, _y in coordArray:
            _board[(_y + dy) * self.board_data_width + _x] = Shape_class.shape
        return _board

    def calcEvaluationValueSample(self, board, pre_isolatedblocks, Shape_class):
        #
        # sample function of evaluate board.
        #
        width = self.board_data_width
        height = self.board_data_height

        # evaluation paramters
        ## lines to be removed
        fullLines = 0
        ## number of holes or blocks in the line.
        nHoles, nIsolatedBlocks = 0, 0
        ## absolute differencial value of MaxY
        absDy = 0
        ## how blocks are accumlated
        BlockMaxY = [0] * width
        holeCandidates = [0] * width
        holeConfirm = [0] * width
        hole_max_height = [0] * width

        x_isolatedblock = 0

        fullLines_para = 3.0
        nHoles_para = 50.0
        nIsolatedBlocks_para = 200.0
        absDy_para = 30.0
        hole_max_height_para = 5.0
        max_height_para = 5.0

        score = 0

        # if pre_isolatedblocks > 0:
        #     fullLines_para = 5.0
        #     nHoles_para = 10.0
        #     nIsolatedBlocks_para = 50.0
        #     absDy_para = 10.0

        ### check board
        # each y line
        for y in range(height - 1, 0, -1):
            hasHole = False
            hasBlock = False
            # each x line
            for x in range(width):
                ## check if hole or block..
                if board[y * self.board_data_width + x] == self.ShapeNone_index:
                    # hole
                    hasHole = True
                    holeCandidates[x] += 1  # just candidates in each column..
                else:
                    # block
                    hasBlock = True
                    BlockMaxY[x] = height - y                # update blockMaxY
                    if holeCandidates[x] > 0:
                        holeConfirm[x] += holeCandidates[x]  # update number of holes in target column..
                        holeCandidates[x] = 0                # reset
                    if holeConfirm[x] > 0:
                        nIsolatedBlocks += 1                 # update number of isolated blocks
                        hole_max_height[x] = BlockMaxY[x]
                        x_isolatedblock += 1

            if hasBlock == True and hasHole == False:
                # filled with block
                fullLines += 1
                if x_isolatedblock > 0:
                    nIsolatedBlocks -= x_isolatedblock
                    x_isolatedblock = 0
            elif hasBlock == True and hasHole == True:
                # do nothing
                pass
            elif hasBlock == False:
                # no block line (and ofcourse no hole)
                pass

        # nHoles
        for x in holeConfirm:
            nHoles += abs(x)

        ### absolute differencial value of MaxY
        BlockMaxDy = []
        for i in range(len(BlockMaxY) - 1):
            val = BlockMaxY[i] - BlockMaxY[i+1]
            BlockMaxDy += [val]
        for x in BlockMaxDy:
            absDy += abs(x)

        #### maxDy
        #maxDy = max(BlockMaxY) - min(BlockMaxY)
        #### maxHeight
        maxHeight = max(BlockMaxY) - fullLines

        ## statistical data
        #### stdY
        #if len(BlockMaxY) <= 0:
        #    stdY = 0
        #else:
        #    stdY = math.sqrt(sum([y ** 2 for y in BlockMaxY]) / len(BlockMaxY) - (sum(BlockMaxY) / len(BlockMaxY)) ** 2)
        #### stdDY
        #if len(BlockMaxDy) <= 0:
        #    stdDY = 0
        #else:
        #    stdDY = math.sqrt(sum([y ** 2 for y in BlockMaxDy]) / len(BlockMaxDy) - (sum(BlockMaxDy) / len(BlockMaxDy)) ** 2)

        # if maxHeight > 11:
        #     absDy_para = 50.0
        #     max_height_para = 50.0

        # if Shape_class.shape == 1 and fullLines <= 2:
        #     score -= 1000

        # calc Evaluation Value
        score = score + fullLines * fullLines_para           # try to delete line
        score = score - nHoles * nHoles_para               # try not to make hole
        score = score - nIsolatedBlocks * nIsolatedBlocks_para      # try not to make isolated block
        # for hole_max_height_column in hole_max_height:
        #     score = score - hole_max_height_column * hole_max_height_para
        score = score - absDy * absDy_para                # try to put block smoothly # yの絶対値を少なくする、ボコボコにしない
        #score = score - maxDy * 0.3                # maxDy
        # score = score - maxHeight * max_height_para              # maxHeight
        #score = score - stdY * 1.0                 # statistical data
        #score = score - stdDY * 0.01               # statistical data

        # print(score, fullLines, nHoles, nIsolatedBlocks, maxHeight, stdY, stdDY, absDy, BlockMaxY)
        return score, nIsolatedBlocks


BLOCK_CONTROLLER_SAMPLE = Block_Controller()
