class GameState:
    def __init__(self):
        self.boardTest = [
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["bN", "--", "bK", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "wp", "--"],
            ["--", "wR", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "wK", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"]
        ]
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {'p': self.getPawnMoves,
                              'R': self.getRookMoves,
                              'B': self.getBishopMoves,
                              'N': self.getKnightMoves,
                              'Q': self.getQueenMoves,
                              'K': self.getKingMoves}
        self.whiteToMove = True
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.enPassantPossible = ()
        self.moveLog = []
        self.knightDirections = ((2, 1), (2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2), (-2, -1), (-2, 1))
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castlingRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                               self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        # update king's position
        if move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        # enpassant

        # update if enpassant can be made if other move than 2 square advance is made
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.endRow + move.startRow) // 2, move.endCol)
        else:
            self.enPassantPossible = ()

        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'  # capturing the pawn

        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # kingside castle
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]  # moves the rook
                self.board[move.endRow][move.endCol + 1] = "--"
            else:  # queenside castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"

        self.updateCastleRights(move)
        self.castlingRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                                   self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))

        # update castling rights

    def undoMove(self, ):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)

            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"  # leave the landing square empty
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enPassantPossible = (move.endRow, move.endCol)

            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enPassantPossible = ()

            # undo castling rights
            self.castlingRightsLog.pop()
            newCastlingRights = self.castlingRightsLog[-1]
            self.currentCastlingRights = CastleRights(newCastlingRights.wks, newCastlingRights.bks,
                                                      newCastlingRights.bks, newCastlingRights.bqs)

            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # kingside
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.bks = False

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = []
        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # reset possible pins)
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':  # phantom king
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        typeOfPiece = endPiece[1]
                        # 5 typeOfPieces of pieces so we need to consider them all
                        if ((0 <= j <= 3 and typeOfPiece == 'R') or (4 <= j <= 7 and typeOfPiece == 'B') or
                                (i == 1 and typeOfPiece == 'p' and (
                                        (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5)))
                                or typeOfPiece == 'Q' or (i == 1 and typeOfPiece == 'K')):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                        else:
                            break
                else:
                    break  # off board

        for d in self.knightDirections:
            endRow = startRow + d[0]
            endCol = startCol + d[1]
            if 0 < endRow < 8 and 0 < endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, d[0], d[1]))
        return inCheck, pins, checks

    def getValidMoves(self):
        moves = []
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                        self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []  # where the king can move to
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]  # can move only to take the Knight
                else:
                    for i in range(1, 8):  # add if the square is on board
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:  # double check - King has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()

        if self.whiteToMove:
            self.getCastlingMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastlingMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True

        self.currentCastlingRights = tempCastleRights

        return moves

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)  # calls for the dictionary
        return moves

    def checkPinnedPiece(self, r, c):
        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        return piecePinned, pinDirection

    def getPawnMoves(self, r, c, moves):
        piecePinned, pinDirection = self.checkPinnedPiece(r, c)

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            enemyColor = 'b'
        else:
            moveAmount = 1
            startRow = 1
            enemyColor = 'w'

        if self.board[r + moveAmount][c] == '--':
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((r, c), (r + moveAmount, c), self.board))
                if r == startRow and self.board[r + 2 * moveAmount][c] == '--':
                    moves.append(Move((r, c), (r + 2 * moveAmount, c), self.board))
        if c - 1 >= 0:
            if self.board[r + moveAmount][c - 1][0] == enemyColor:
                if not piecePinned or pinDirection == (moveAmount, -1):
                    moves.append(Move((r, c), (r + moveAmount, c - 1), self.board))
            elif (r + moveAmount, c - 1) == self.enPassantPossible:
                moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, isEnpassantMove=True))
        if c + 1 <= 7:
            if self.board[r + moveAmount][c + 1][0] == enemyColor:
                if not piecePinned or pinDirection == (moveAmount, 1):
                    moves.append(Move((r, c), (r + moveAmount, c + 1), self.board))
            elif (r - 1, c + 1) == self.enPassantPossible:
                moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, isEnpassantMove=True))

    def getRookMoves(self, r, c, moves):

        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, 1), (1, 0), (0, -1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endCol <= 7 and 0 <= endRow <= 7:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # friendly piece - don't look in that direction anymore
                            break
                else:  # not on the board - don't look in that direction anymore
                    break

    def getKingMoves(self, r, c, moves):
        directions = ((1, 1), (1, -1), (1, 0), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endCol <= 7 and 0 <= endRow <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

    def getKnightMoves(self, r, c, moves):
        enemyColor = 'b' if self.whiteToMove else 'w'
        piecePinned = False
        # pinDirection = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        for d in self.knightDirections:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endCol <= 7 and 0 <= endRow <= 7:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == enemyColor or endPiece[0] == '-':
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getBishopMoves(self, r, c, moves):
        piecePinned, pinDirection = self.checkPinnedPiece(r, c)

        directions = ((-1, 1), (1, 1), (1, -1), (-1, -1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endCol <= 7 and 0 <= endRow <= 7:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # friendly piece - don't look in that direction anymore
                            break
                else:  # not on the board - don't look in that direction anymore
                    break

    def getCastlingMoves(self, r, c, moves):
        if self.inCheck:
            return
        if (self.whiteToMove and self.currentCastlingRights.wks) or (
                not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (
                not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

        # Pawn promotion
        self.isPawnPromotion = (self.endRow == 0 and self.pieceMoved == 'wp') or (
                self.endRow == 7 and self.pieceMoved == 'bp')
        # Enpassant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'bp' if self.pieceMoved == 'wp' else 'wp'

        # Castling

        self.isCastleMove = isCastleMove

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    '''Overriding equals'''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
