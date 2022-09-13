import pygame, sys, os
class Board:
  orthagonal = {8, -1, 1, -8}
  diagonal = {-9, 9, 7, -7}
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
    for name in ["move", "aimove", "capture", "check", "castle", "promote"]:
      path = os.path.join(os.path.dirname(__file__),"Assets\\Audio\\"+name+".wav")
      self.sounds[name] =  pygame.mixer.Sound(path)
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
    #TODO: OPTIMIZE USING SORTED BINARY SEARCH AT SOME POINT
    if original == new:
      return
    if self.squares[new]:
      pygame.mixer.Sound.play(self.sounds["capture"])
    else:
      pygame.mixer.Sound.play(self.sounds["move"])
    self.squares[new] = self.squares[original]
    
    self.squares[original] = 0
    self.pieces.discard(original)
    self.pieces.add(new)
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
    moves = [[] for i in range(64)]
    for piece in self.pieces:
      if self.squares[piece] // 8 != self.turn:
        pass
      #continue soon
      if self.squares[piece] % 8 == 5 or self.squares[piece] % 8 == 6:
        #rook or queen, orthoganal
        file, rank = Board.stfr(piece)
        s = piece
        for i in range(file):
          #left
          s -= 1
          moves[piece].append(s)
        s = piece
        for i in range(7 - file):
          #right
          s += 1
          moves[piece].append(s)
        s = piece
        for i in range(rank):
          #down
          s -= 8
          moves[piece].append(s)
        s = piece
        for i in range(7 - rank):
          #up
          s += 8
          moves[piece].append(s)          
      if self.squares[piece] % 8 == 4 or self.squares[piece] % 8 == 6:
        #bishop or queen, diagonal
        file, rank = Board.stfr(piece)
        s = piece
        for i in range(min(file, rank)):
          #left-down
          s -= 9
          moves[piece].append(s)
        s = piece
        for i in range(min(7 - file, rank)):
          #right-down
          s -= 7
          moves[piece].append(s)
        s = piece
        for i in range(min(file, 7 - rank)):
          #left-up
          s += 7
          moves[piece].append(s)
        s = piece
        for i in range(min(7 - file, 7 - rank)):
          s += 9
          moves[piece].append(s)
        pass
        
      if self.squares[piece] % 8 == 7:
        pass

      if self.squares[piece] % 8 == 3:
        pass

      if self.squares[piece] % 8 == 1:
        pass
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
board.displayBoard(screen, pygame.mouse.get_pos())
pygame.display.update()
while True:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
    if event.type == pygame.MOUSEBUTTONDOWN:
      board.click(pygame.mouse.get_pos())
    if event.type == pygame.MOUSEBUTTONUP:
      board.release(pygame.mouse.get_pos())
  board.displayBoard(screen, pygame.mouse.get_pos())
  pygame.display.update()


    

        

