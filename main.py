import pygame, sys, os
class Board:
  def __init__(self):
    self.squares = [0]*64
    self.selected = None
    self.light = (250,230,210)
    self.dark = (155,115,95)
    self.highlight = (255,255,0)
    self.held = False
    self.cancel = False
    self.sounds = dict()
    self.pieces = set()
    self.turn = 0
    self.legalPointer = (200, 200, 200)
    self.enPassant = None
    for name in ["move", "aimove", "capture", "check", "castle", "promote"]:
      path = os.path.join(os.path.dirname(__file__),"Assets\\Audio\\"+name+".wav")
      self.sounds[name] =  pygame.mixer.Sound(path)
    self.castleRights = [True, True, True, True]
    self.moves = [[] for i in range(64)]
  def getPiece(self, square):
    return self.squares[square]
  def frts(f, r):
    return f + r*8
  def stfr(square):
    return (square%8, square//8)
  def displayBoard(self, screen, pos):
    for s in range(len(self.squares)):
      f, r = Board.stfr(s)
      if (f+r)%2:
        color = self.light
      else:
        color = self.dark
      if s == self.selected:
        color = Board.colorBlending(color, self.highlight, .60)
      pygame.draw.rect(screen, color, (f*80,(7-r)*80,80,80))
      if self.squares[s] and not (s == self.selected and self.held):
          screen.blit(sprites[self.squares[s]],(f*80,(7-r)*80))
      if self.selected != None and s in self.moves[self.selected]:
        pygame.draw.circle(screen, self.legalPointer, (f*80 + 40, (7-r)*80 + 40), 15)
    if self.held and self.selected != None:
      screen.blit(sprites[self.squares[self.selected]], (pos[0]-40,pos[1]-40))
  def infr(pos):
    f = pos[0]//80
    r = 7-pos[1]//80
    return (f,r)
  def move(self, original, new):
    enPassanting = False
    castling = 0
    if not new in self.moves[original]:
      return
    if self.enPassant and new == self.enPassant and self.squares[original]%8==1:
      enPassanting = True
    if original//8 == self.turn*5+1 and self.squares[original] % 8 == 1 and new == original + 16 - 32 * self.turn:
      self.enPassant = original + 8 - 16 * self.turn
    else:
      self.enPassant = None
    if self.squares[original] % 8 == 7:
      self.castleRights[self.turn * 2] = False
      self.castleRights[self.turn * 2 + 1] = False
      if new - original == 2 or new - original == -2:
        castling = 1 + (new - original + 2)//4 
    if original == 0 or new == 0:
      self.castleRights[0] = False
    if original == 7 or new == 7:
      self.castleRights[1] = False
    if original == 56 or new == 56:
      self.castleRights[2] = False
    if original == 63 or new == 63:
      self.castleRights[3] = False
    if self.squares[new] or enPassanting:
      pygame.mixer.Sound.play(self.sounds["capture"])
    else:
      pygame.mixer.Sound.play(self.sounds["move"])
    self.squares[new] = self.squares[original]
    self.squares[original] = 0
    self.pieces.discard(original)
    self.pieces.add(new)
    if enPassanting:
      self.squares[new - 8 + self.turn * 16] = 0
      self.pieces.discard(new - 8 + self.turn * 16)
    if castling:
      x = self.turn * 56
      if castling == 1:
        self.squares[x + 3] = self.squares[x]
        self.squares[x] = 0
        self.pieces.discard(x)
        self.pieces.add(x+3)
      if castling == 2:
        self.squares[x + 5] = self.squares[x + 7]
        self.squares[x + 7] = 0
        self.pieces.discard(x + 7)
        self.pieces.add(x+5)
    self.turn = 1 - self.turn
    self.generateMoves()
  def inSquare(pos):
    return Board.frts(*Board.infr(pos))
  def fenConverter(self, fen):
    pos = fen[0:fen.find(" ")].split("/")
    squares = [0]*64
    pieceNames = {"p": 1, "n": 3, "b": 4, "r": 5, "q": 6, "k": 7}
    pieces = set()
    i = 0
    for r in reversed(pos):
      t = i
      for p in r:
        if p.isdigit():
          i += int(p)
        else:
          if p.lower() in pieceNames:
            squares[i] = 8*p.islower() + pieceNames[p.lower()]
            pieces.add(i)
            i += 1
          else:
            print("Fen Conversion Error: Bad Character")
            return 1
      if t != i - 8:
        print("Fen Conversion Error: Bad Spacing")
        return 1
    self.squares = squares
    self.pieces = pieces
    self.generateMoves()
  def colorBlending(c1, c2, p):
    return ((1-p)*c1[0] + p*c2[0], (1-p)*c1[1] + p*c2[1], (1-p)*c1[2] + p*c2[2])
  def click(self, pos):
    square = Board.inSquare(pos)
    self.held = True
    if self.selected != None:
      if self.selected == square and self.selected != None:
        self.cancel = True
      else:
        self.move(self.selected, square)
        self.selected = None
    elif self.squares[square]:
      self.selected = square
  def release(self, pos):
    if self.selected == None:
      return
    square = Board.inSquare(pos)
    if square == self.selected and self.cancel:
      self.selected = None
    elif square != self.selected:
      self.move(self.selected, square)
      self.selected = None
    self.held = False
    self.cancel = False
  def generateMoves(self):
    moves = [set() for i in range(64)]
    for piece in self.pieces:
      if self.squares[piece] // 8 != self.turn:
        continue
      file, rank = Board.stfr(piece)
      if self.squares[piece] % 8 == 5 or self.squares[piece] % 8 == 6 or self.squares[piece] % 8 == 7:
        #rook, queen, or king, orthoganal
        s = piece
        for i in range(file):
          #left
          s -= 1
          if self.squares[s] and self.squares[s] // 8 == self.turn:
            break
          moves[piece].add(s)
          if self.squares[piece] % 8 == 7 or self.squares[s] and self.squares[s] // 8 != self.turn:
            break
        s = piece
        for i in range(7 - file):
          #right
          s += 1
          if self.squares[s] and self.squares[s] // 8 == self.turn:
            break
          moves[piece].add(s)
          if self.squares[piece] % 8 == 7 or self.squares[s] and self.squares[s] // 8 != self.turn:
            break
        s = piece
        for i in range(rank):
          #down
          s -= 8
          if self.squares[s] and self.squares[s] // 8 == self.turn:
            break
          moves[piece].add(s)
          if self.squares[piece] % 8 == 7 or self.squares[s] and self.squares[s] // 8 != self.turn:
            break
        s = piece
        for i in range(7 - rank):
          #up
          s += 8
          if self.squares[s] and self.squares[s] // 8 == self.turn:
            break
          moves[piece].add(s)
          if self.squares[piece] % 8 == 7 or self.squares[s] and self.squares[s] // 8 != self.turn:
            break
      if self.squares[piece] % 8 == 4 or self.squares[piece] % 8 == 6 or self.squares[piece] % 8 == 7:
        #bishop, queen, or king, diagonal
        s = piece
        for i in range(min(file, rank)):
          #left-down
          s -= 9
          if self.squares[s] and self.squares[s] // 8 == self.turn:
            break
          moves[piece].add(s)
          if self.squares[piece] % 8 == 7 or self.squares[s] and self.squares[s] // 8 != self.turn:
            break
        s = piece
        for i in range(min(7 - file, rank)):
          #right-down
          s -= 7
          if self.squares[s] and self.squares[s] // 8 == self.turn:
            break
          moves[piece].add(s)
          if self.squares[piece] % 8 == 7 or self.squares[s] and self.squares[s] // 8 != self.turn:
            break
        s = piece
        for i in range(min(file, 7 - rank)):
          #left-up
          s += 7
          if self.squares[s] and self.squares[s] // 8 == self.turn:
            break
          moves[piece].add(s)
          if self.squares[piece] % 8 == 7 or self.squares[s] and self.squares[s] // 8 != self.turn:
            break
        s = piece
        for i in range(min(7 - file, 7 - rank)):
          s += 9
          if self.squares[s] and self.squares[s] // 8 == self.turn:
            break
          moves[piece].add(s)
          if self.squares[piece] % 8 == 7 or self.squares[s] and self.squares[s] // 8 != self.turn:
            break
      if self.squares[piece] % 8 == 3:
        #Knight
        for i in [2, -2]:
          for j in [1, -1]:
            if file + i < 8 and file + i >= 0 and rank + j < 8 and rank + j >= 0:
              s = Board.frts(file + i, rank + j)
              if not (self.squares[s] and self.squares[s] // 8 == self.turn):
                moves[piece].add(s)
            if rank + i < 8 and rank + i >= 0 and file + j < 8 and file + j >= 0:
              s = Board.frts(file + j, rank + i)
              if not (self.squares[s] and self.squares[s] // 8 == self.turn):
                moves[piece].add(s)
      if self.squares[piece] % 8 == 1:
        #Pawn
        #Regular moves
        direct = 1 - self.turn*2
        s = piece + 8 * direct
        if not s > 63 or s < 0:
          #Forward Moves
          if not self.squares[s]:
            moves[piece].add(s)
            #Move forward twice check
            s = s + 8 * direct
            if rank == 1 + 5 * self.turn and not self.squares[s]:
              moves[piece].add(s)
          #Captures
          s = piece + 8 * direct
          f, r = Board.stfr(s)
          #Capture to the left
          if f > 0:
            s = Board.frts(f - 1, r)
            if s == self.enPassant or (board.squares[s] and board.squares[s]//8 != self.turn):
              moves[piece].add(s)
            
          #Capture to the right
          if f < 7:
            s = Board.frts(f + 1, r)
            if s == self.enPassant or (board.squares[s] and board.squares[s]//8 != self.turn):
              moves[piece].add(s)
      s = piece
      if self.squares[piece] % 8 == 7:
        #That good old castle
        r = self.turn*56
        if self.castleRights[self.turn*2]:
          qLegal = True
          for i in range(1, 4):
            if self.squares[r + i]:
              qLegal = False
              break
          if qLegal:
            moves[piece].add(s - 2)
        if self.castleRights[self.turn*2 + 1]:
          kLegal = True
          for i in range(5,7):
            if self.squares[r + i]:
              kLegal = False
              break
          if kLegal:
            moves[piece].add(s + 2)
          
          
          
    self.moves = moves        
    
  

    
    
        
          
          
      
      
"""
Piece Values
None: 0
Pawn: 1
Spare Piece: 2
Knight: 3
Bishop: 4
Rook: 5
Queen: 6
King: 7
"""
pygame.init()
pygame.mixer.init()

sprites = []
for i in range(16):
  n = i
  if i%8 == 2:
    n -= 1
  
  if i%8 == 0:
    n = None
  else:
    n = pygame.image.load(os.path.join(os.path.dirname(__file__),"Assets\\Pieces\\"+str(n)+".png"))
    n = pygame.transform.smoothscale(n, (80,80))
  sprites.append(n)




screen = pygame.display.set_mode((640, 640))
board = Board()
board.fenConverter("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0")
running = True
while running:
  board.displayBoard(screen, pygame.mouse.get_pos())
  pygame.display.update()
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      running = False
      break
    if event.type == pygame.MOUSEBUTTONDOWN:
      board.click(pygame.mouse.get_pos())
    if event.type == pygame.MOUSEBUTTONUP:
      board.release(pygame.mouse.get_pos())




    

        

