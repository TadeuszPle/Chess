import pygame as p
import ChessAI
from Chess import ChessEngine

BOARD_WIDTH = BOARD_HEIGHT = 512  # 400 OTHER GOOD OPTION
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8  # Board is 8x8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15  # for animations later on
IMAGES = {}


# Initialize a global dictionary of images. This will be called only once in main

def load_images():
    # IMAGES['wp'] = p.image.load("images/wp.png")
    pieces = ["bR", "bN", "bB", "bQ", "bK", "wR", "wN", "wB", "wQ", "wK", "bQ", "bp", "wp"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('images/' + piece + '.png'), (SQ_SIZE, SQ_SIZE))
        # note - we can access an image by saying 'IMAGES'['wp']


def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont = p.font.SysFont("Arial", 16, True, False)
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    gameOver = False
    load_images()
    sqSelected = ()  # last click of the user
    playerClicks = []  # keeps track of player clicks  - two tuples
    running = True
    playerOne = True  # if a human is white this is True
    playerTwo = True  # if a human is black  this is True
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col) or col > 7:  # deselect when clicking twice or clicking on the move log
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:  # after 2nd click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo a move when z is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False  # don't animate after a undo
                    gameOver = False
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    gs.whiteToMove = True
                    gameOver = False
                    animate = False
                    moveMade = False
        # AI move finder
        if not gameOver and not humanTurn:
            AIMove = ChessAI.findBestMove(gs, validMoves)
            if AIMove is None:
                print("no moves found?")
                AIMove = ChessAI.findRandomMove(validMoves)
                for move in validMoves:
                    print(move)
                print("no moves found?")
                print(AIMove)
            # AIMove = ChessAI.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)

        if not gameOver:
            drawMoveLog(screen, gs, moveLogFont)

        if gs.checkmate or gs.stalemate:
            gameOver = True
            text = "Draw by stalemate" if gs.stalemate else 'Black won by checkmate' if gs.whiteToMove else 'White won by checkmate'
            drawEndGameText(screen, text)

        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)

def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))



def highlightSquares(screen, gs, validMoves, sqSelected):
    # highlight last move
    if len(gs.moveLog) != 0:
        lastMove = gs.moveLog[-1]
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(70)
        s.fill(p.Color('orange'))
        screen.blit(s, (lastMove.startCol * SQ_SIZE, lastMove.startRow * SQ_SIZE))
        screen.blit(s, (lastMove.endCol * SQ_SIZE, lastMove.endRow * SQ_SIZE))

    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency setting
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # highlight moves form that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))



def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, 0, p.Color("Black"))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2,
                                                                BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Blue"))
    screen.blit(textObject, textLocation.move(2, 2))



def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2+1) + ". " + str(moveLog[i])+ " "
        if i+1 < len(moveLog):
            moveString += str(moveLog[i+1])
        moveTexts.append(moveString)
    padding = 5
    for i in range(len(moveTexts)):
        text = moveTexts[i]
        textObject = font.render(text, True, p.Color("white"))
        textLocation = moveLogRect.move(padding, padding*3*i)
        screen.blit(textObject, textLocation)

'''
Animating a move
'''


def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # erease the piece moved from the ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)  # location of end square
        p.draw.rect(screen, color, endSquare)
        # draw a captured piece back
        if move.pieceCaptured != '--':
            if move.enpassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == "b" else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw the moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
