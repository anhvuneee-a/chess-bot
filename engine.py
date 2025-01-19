from copy import deepcopy

# Chess board:
class ChessBoard:
 def __init__(self,board=None,show_none=True,update_next=[]):
  # Board can be None if an empty board is needed.
  # show_none: if True, all empty pieces render as '--'
  # kings: important keys. Only used for Kings.
  # update_next: Keys to update next move.
  self.board=[
   ["","","","","","","",""],
   ["","","","","","","",""],
   ["","","","","","","",""],
   ["","","","","","","",""],
   ["","","","","","","",""],
   ["","","","","","","",""],
   ["","","","","","","",""],
   ["","","","","","","",""]]
  self.show_none=show_none
  self.kings=[]
  self.update_next=update_next
  if isinstance(board,str):
   board=board.strip().split("/")
   for x,row in enumerate(board):
    y=-1
    for col in row:
     data=""
     if col in "12345678":
      for i in range(int(col)):
       y+=1
       self.board[x][y]=ChessPiece(show_none=self.show_none).setloc([x,y])
     else:
      y+=1
      piece=NewPiece("wb"[col.islower()]+col.upper(),self,self.show_none)
      self.board[x][y]=piece.setloc([x,y])
      if piece.key=="K": self.kings.append(piece)
  elif board is not None:
   for x in range(8):
    for y in range(8):
     piece=NewPiece(board[x][y],self,self.show_none)
     self.board[x][y]=piece.setloc([x,y])
     if piece.key=="K": self.kings.append(piece)
  else:
   for x in range(8):
    for y in range(8):
     piece=ChessPiece(show_none=self.show_none)
     self.board[x][y]=piece.setloc([x,y])
 def __repr__(self):
  return '\n'.join([' '.join([str(k) for k in i]) for i in self.board])
 # Gets the piece/pieces according to the address:
 def __getitem__(self,address):
  # If using Location class: get the pos and returns the board entry.
  if isinstance(address,Location): 
   x,y=address.pos
   return self.board[x][y]
  case=len(address)
  # Diagonal style:
  if case==3:
   ds=address[-1]
   addr=address[:2]
   pos=Location(addr).pos
   index=0
   # / diag
   if ds == "+":
    # Move up the line until the top is reached:
    while not (pos[0]==0 or pos[1]==7):
     pos[0]-=1
     pos[1]+=1
     index+=1
    values=[]
    # Moves down the line, adding entries as we go:
    while not (pos[0]==8 or pos[1]==-1):
     values.append(self.board[pos[0]][pos[1]])
     pos[0]+=1
     pos[1]-=1
    return ChessBoardDiag(self,values,addr,ds,index)
   # \ diag
   if ds == "-":
    # Move up the line until the top is reached:
    while not (pos[0]==0 or pos[1]==0):
     pos[0]-=1
     pos[1]-=1
     index+=1
    values=[]
    # Moves down the line, adding entries as we go:
    while not (pos[0]==8 or pos[1]==8):
     values.append(self.board[pos[0]][pos[1]])
     pos[0]+=1
     pos[1]+=1
    return ChessBoardDiag(self,values,addr,ds,index)
  # Address style:
  elif case==2:
   address=list(address)
   return self[address[0]][address[1]]
  # Row/column style:
  elif case==1:
   # Gets all pieces in this row:
   if address in "12345678":
    row=8-int(address)
    return ChessBoardRow(self,self.board[row],address)
   # Gets all pieces in this column:
   elif address in "abcdefgh":
    column="abcdefgh".find(address)
    column=[row[column] for row in self.board]
    return ChessBoardColumn(self,column,address)
   # Invalid row/column style:
   else:
    raise Exception('Invalid row/column address style:',address)
  # Invalid address format:
  else:
   raise Exception('Invalid address:',address)
 # Assign new pieces with ChessBoard[loc]=piece:
 def __setitem__(self,loc,piece):
  # Evaluates location into usable format:
  if not isinstance(loc,Location): loc=Location(loc)
  x,y=loc.pos
  # Creates a new chess piece based on given piece data:
  if isinstance(piece,str): 
   piece=NewPiece(piece,self,self.show_none).setloc(loc)
  # Adds piece to chessboard:
  self.board[x][y]=piece
 # Useful if someone's running "for piece in chessboard":
 def __iter__(self):
  return iter(item for row in self.board for item in row)
 # Move selection stuff:
 def options(self,side):
  ans={"options":0,"moves":{}}
  for piece in self:
   if piece.side==side:
    moves=piece.moves(True)
    if moves:
     ans["moves"]|={piece.loc.addr:moves}
     ans["options"]+=len(moves)
  return ans
 def strength(self,side):
  ans={"strength":0,"pieces":[]}
  strengths={"P":-1,"R":-10,"B":-5,"N":-5,"Q":-20,"K":0}
  for piece in self:
   if piece.side==side:
    ans["pieces"].append(piece)
    ans["strength"]+=strengths[piece.key]
  return ans
 def control(self,side):
  tile_values=[
   [1,2,3,4,4,3,2,1],
   [2,3,4,5,5,4,3,2],
   [3,4,5,6,6,5,4,3],
   [4,5,6,9,9,6,5,4],
   [4,5,6,9,9,6,5,4],
   [3,4,5,6,6,5,4,3],
   [2,3,4,5,5,4,3,2],
   [1,2,3,4,4,3,2,1]]
  ans={"options":0,"control":0}
  piece_values={"P":-1,"R":-4,"N":-3,"B":-3,"Q":-10,"K":0}
  options=self.options(side)
  ans["options"]=options["options"]
  options=options["moves"]
  for piece in options:
   moves=options[piece]
   loc=Location(piece)
   pos=loc.pos
   piece_val=piece_values[self[loc].key]
   piece_control=tile_values[pos[0]][pos[1]]*piece_val
   for move in moves:
    dst=move.pos
    piece_control+=tile_values[dst[0]][dst[1]]*piece_val
   ans["control"]+=piece_control
  return ans

class ChessBoardRow:
 def __init__(self,table,values,row):
  self.table=table
  self.values=values
  self.row=row
  self.loc=[i.loc for i in values]
 def __repr__(self):
  return " ".join([str(i) for i in self.values])
 def __getitem__(self,column):
  c="abcdefgh".find(column)
  if column == -1: 
   raise Exception('Invalid column:',column)
  return self.values[c]
 # If a piece is in this row:
 def __contains__(self,piece):
  return piece in self.values
 # Useful for "for i in ChessBoardRow"
 def __iter__(self):
  return iter(self.values)
class ChessBoardColumn:
 def __init__(self,table,values,column):
  self.table=table
  self.values=values
  self.column=column
  self.loc=[i.loc for i in values]
 def __repr__(self):
  return "\n".join(["--" if not i else str(i) for i in self.values])
 # If a piece is in this column:
 def __contains__(self,piece):
  return piece in self.values
 def __getitem__(self,row):
  try:
   r=row=8-int(row)
  except ValueError:
   raise Exception('Invalid row:',row)
  return self.values[r]
 # Useful for "for i in ChessBoardColumn"
 def __iter__(self):
  return iter(self.values)
class ChessBoardDiag:
 def __init__(self,table,values,tile,direction,index):
  self.table=table
  self.values=values
  self.tile=tile
  self.direction=direction
  self.index=index
  self.loc=[i.loc for i in values]
 def __repr__(self):
  size=len(self.values)
  reftable=[["  " for j in range(size)] for i in range(size)]
  # Note: Reading order: topdown, following slash
  # forward slash: /
  if self.direction=="+":
   for num,i in enumerate(self.values):
    reftable[num][size-1-num]=i
   return '\n'.join([" ".join(['--' if k is None else str(k) for k in i]) for i in reftable])
  # backward slash: \
  else:
   for num,i in enumerate(self.values):
    reftable[num][num]=i
   return '\n'.join([" ".join(['--' if k is None else str(k) for k in i]) for i in reftable])
  return ""
 # Useful for "for i in ChessBoardColumn"
 def __iter__(self):
  return iter(self.values)
# Location class for handling chess board locations:
class Location:
 def __init__(self,data):
  self.data=data
  if isinstance(data,Location):
   self.pos=data.pos
   self.addr=data.addr
  elif isinstance(data,str):
   self.addr=data
   self.pos=self.to_pos()
  elif isinstance(data,(tuple,list)):
   data=list(data)
   self.pos=data
   self.addr=self.to_addr()
 def __repr__(self):
  return self.addr
 def __eq__(self,b):
  return self.pos==b.pos
 # Indexing a location class: Index its address instead.
 def __getitem__ (self,index):
  return self.addr[index]
 def __hash__(self):
  return hash(self.addr)
 def to_pos(self):
  try:
   return [8-int(self.data[1]),"abcdefgh".find(self.data[0])]
  except IndexError:
   raise Exception('Invalid address:',self.data)
 def to_addr(self):
  return f'{"abcdefgh"[self.data[1]]}{8-int(self.data[0])}'
 def update(self,data):
  self.__init__(data)

# Chess Moves:
class ChessMoves:
 def __init__(self,piece,moves):
  if moves: self.moves=[Location(i) for i in moves]
  else: self.moves=[]
  self.piece=piece
 # Adding 2 ChessMoves classes together with a+b:
 def __add__(self,b):
  self.moves+=b.moves
  return self
 def __repr__(self):
  return repr(self.moves)
 # If has moves: True, False otherwise:
 def __bool__(self):
  return bool(self.moves)
 # See if a location is in the list of moves:
 def __contains__(self,addr):
  addr=Location(addr)
  return addr in self.moves
 # Point a move with Moves[index]:
 def __getitem__(self,index):
  return self.moves[index]
 # Useful for doing for i in ChessMoves:
 def __iter__(self):
  return iter(self.moves)
 # Filter similar moves from 2 ChessMoves classes:
 def __and__(self,b):
  return set(self.moves)&set(b.moves)
 def __hash__(self):
  return hash(tuple(sorted(self.moves)))
 def __len__(self):
  return len(self.moves)
 # See which move has a piece on it:
 def has_piece(self):
  table=self.piece.table
  ans=[]
  for move in self.moves:
   piece=table[move.addr]
   if piece: ans.append(piece)
  return ans
 # A quick visual on an empty ChessBoard for testing:
 def visualize(self):
  visboard=ChessBoard(show_none=False)
  table=self.piece.table
  for move in self.moves:
   if not table[move.addr]: visboard[move.addr]=ChessPiece(True)
   else: visboard[move.addr]=table[move.addr]
  return visboard
# Special class for king checks:
class Checked:
 def __init__(self,by,src=None,path=None):
  # by: list of checkers
  # src: location that got checked.
  # path: The attack path of the attackers.
  self.by=by
  self.src=src
  self.path=path
 def __repr__(self):
  if not self: return "Not Checked!"
  else: return f'Checked!\nSources:{self.by}'
 def __bool__(self):
  return bool(self.by)
 def __iter__(self):
  return iter(self.by)
 # Visualizes all checked sources:
 def visualize(self):
  visboard=ChessBoard(show_none=False)
  table=self.by[0].table
  visboard[self.src]=ChessPiece(True)
  for checker in self:
   visboard[checker.loc]=table[checker.loc]
  return visboard

# A chess piece that essentially represents nothing.
# Is used in code queries to return a None wherever it's used.
class ChessPiece:
 def __init__(self,show_none=False):
  self.loc=None
  self.key=None
  self.side=None
  self.moved=None # King, Rook, Pawns attribute
  self.table=None
  self.show_none=show_none # If false, empty values are "  " instead of "--"
 def __repr__(self):
  if self.show_none: return "--"
  else: return "  "
 def __str__(self):
  return self.__repr__()
 def setloc(self,loc):
  if not isinstance(loc,Location): loc=Location(loc)
  self.loc=loc
  return self
 def __bool__(self):
  return not self.key is None
 # 2 chess pieces are considered the same if the key and side are the same.
 def __eq__(self,b):
  if not b: return False
  elif isinstance(b,str): return self.key==b[1] and self.side==b[0]
  else: return self.key==b.key and self.side==b.side
 # See if the given address is checked: 
 # (ignore_kings: Ignore king checks, moving: If the piece is moving there)
 def is_checked(self,loc=None,ignore_kings=False,moving=True,record_path=False):
  # If None, uses the king's address.
  if loc is None: loc=self.loc
  else: loc=Location(loc)
  # Saves old piece for later use:
  old_piece=self.table[loc.addr]
  invis_king=self.table[self.loc.addr]
  self.table[self.loc.addr]=""
  by=[]
  path=[]
  
  # As a Rook: Find pieces Rook could take:
  self.table[loc.addr]=self.side+"R"
  pieces=self.table[loc.addr].moves().has_piece()
  # If an enemy Rook or Queen is spotted, it's a check.
  for piece in pieces:
   if piece.key == "R" or piece.key == "Q": 
    by.append(piece)
    if record_path: 
     if piece.key=="Q": path.append((piece.moves(part="R")&self.table[loc.addr].moves())|{piece.loc})
     else: path.append((piece.moves()&self.table[loc.addr].moves())|{piece.loc})
  
  # As a Bishop: Find pieces Bishop could take:
  self.table[loc.addr]=self.side+"B"
  pieces=self.table[loc.addr].moves().has_piece()
  # If an enemy Bishop or Queen is spotted, it's a check.
  for piece in pieces:
   if piece.key == "B" or piece.key == "Q": 
    by.append(piece)
    if record_path:
     if piece.key=="Q": path.append((piece.moves(part="B")&self.table[loc.addr].moves())|{piece.loc})
     path.append((piece.moves()&self.table[loc.addr].moves())|{piece.loc})

  # As a Knight, find pieces Knight could take:
  self.table[loc.addr]=self.side+"N"
  pieces=self.table[loc.addr].moves().has_piece()
  # If an enemy Knight is spotted, it's a check.
  for piece in pieces:
   if piece.key == "N": 
    by.append(piece)
    if record_path: path.append({piece.loc})
    
  # As a Pawn, find pieces Pawn could take:
  self.table[loc.addr]=self.side+"P"
  pieces=self.table[loc.addr].moves().has_piece()
  # If an enemy Pawn is spotted and the piece is actually moving there, it's a check.
  if moving:
   for piece in pieces:
    if piece.key == "P": 
     by.append(piece)
     if record_path: path.append({piece.loc})
  elif not old_piece:
   # If not moving there, Pawns can only move straight to this piece to intercept.
   forward=[1,-1][self.side=="w"]
   x,y=loc.pos
   for i in [1,2]:
    mx=x+forward*i
    if 0<mx<8:
     dst=Location([mx,y])
     piece=self.table[dst]
     if piece.key == "P" and piece.side != self.side:
      if i==2 and piece.moved==0: by.append(piece)
      elif i==1: by.append(piece)
  
  # Looks in surrounding tiles to find a King:
  if not ignore_kings:
   x,y=loc.pos
   moves=[(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
   for move in moves:
    mx,my=x+move[0],y+move[1]
    # If moved positions are valid:
    if -1<mx<8 and -1<my<8:
     target=self.table.board[mx][my]
     # If an enemy King is spotted:
     if target and self.side != target.side and target.key=="K": by.append(piece)
  
  # Returns final checked object:
  self.table[self.loc.addr]=invis_king
  self.table[loc.addr]=old_piece
  return Checked(by,loc,path)
 # Moves a piece with a+b syntax:
 # Returns the move code of that action:
 def __add__(self,addr):
  # Stores backup:
  backup=ChessBoard(self.table.board,self.table.show_none)
  # Gets address and extra information from data:
  addr,extras=addr[:2],addr[2:]
  premoved_dst=self.table[addr]
  premoved_src=self.table[self.loc.addr]
  # Catches all exceptions, if one is raised, loads a backup of the board.
  try:
   # If move isn't valid:
   if addr not in self.moves(): 
    raise Exception(f'Invalid move address: {addr}\nSuggestions: {self.moves()}')
   # Castling cases:
  
   # If not castling:
   # Movement code always includes destination:
   ans=addr
   
   # Captures:
   if premoved_dst: 
    ans="x"+ans
    if premoved_dst.key=="K":
     self.table.kings.remove(premoved_dst)
   # Multiple similar pieces can go to destination: (except from Pawns)
   # Pretends the destination as that piece, on a different side.
   if self.key!="P":
    self.table[addr]="wb"[self.side=="w"]+self.key
    check=self.table[addr]
    # Finds pieces with the same key and add to list:
    check_pieces=[i for i in check.moves().has_piece() if i.key==premoved_src.key]
    # If there are at least 2 pieces with the same key:
    if len(check_pieces)>1:
     # Lists all addresses of the pieces that are the same:
     cache=[i.loc.addr for i in check_pieces]
     src=""
     # Gets the rows and columns of the address list:
     cols=[i[0] for i in cache]
     rows=[i[1] for i in cache]
     # If at least 2 pieces have the same row as source: adds column to src
     if rows.count(premoved_src.loc[1])>1:
      src+=premoved_src.loc[0]
     # If at least 2 pieces have the same column as source: adds row to src
     if cols.count(premoved_src.loc[0])>1: 
      src+=premoved_src.loc[1]
     # If none of the pieces have the same value as source: adds column to src
     if not src: 
      src+=premoved_src.loc[0]
     ans=src+ans
    # If not Pawn, add piece data:
    ans=self.key+ans
   # If Pawn, and a piece has been captured, and the captured column is not set:
   elif ans[0]=="x": 
    ans=self.loc[0]+ans
   
   # Moves piece in the table:
   self.table[addr]=self
   self.table[self.loc.addr]=""
   # Updates moved piece location:
   old_loc=self.loc
   self.loc=Location(addr)

   # Update table pawns:
   while self.table.update_next:
    piece=self.table[self.table.update_next[0]]
    if piece.key == "P": 
     # Pawns that have jumped before are now set to 1.
     piece.moved=1
    del self.table.update_next[0]

   # Special cases:
   # Pawns:
   if self.key=="P":
    # Update moved attribute:
    if not self.moved:
     if abs(int(old_loc[1])-int(self.loc[1]))==2:
      self.moved=2
      self.table.update_next.append(self.loc)
     else: self.moved=1
    # En passant:
    if old_loc[0]!=addr[0] and not premoved_dst:
     caploc=addr[0]+old_loc[1]
     ans=old_loc[0]+"x"+ans
     self.table[caploc]=""
    # Promotion:
    if addr[1]=="18"[self.side=="w"]:
     if not extras: 
      raise Exception('Needs a piece to promote the Pawn!\nAdd one of QRNB to the back of address.')
     elif extras[0] not in "QRNB":
      raise Exception(f'Invalid promotion piece:{extras[0]}\nMust be either Q,R,N,B.')
     self.table[addr]=self.side+extras[0]
     ans+=f"={extras[0]}"
   # Rooks:
   elif self.key=="R":
    # Update moved attribute:
    self.moved=True
   # Kings:
   elif self.key=="K":
    # Update moved attribute:
    self.moved=True
    # Castling cases: (looking for column distance, after-forward)
    horizontal=Location(addr).pos[1]-old_loc.pos[1]
    # Queenside castling:
    if horizontal==-2:
     # Moves the Rook from A to D of the same row:
     rook_src="a"+self.loc[1]
     dest="d"+self.loc[1]
     self.table[dest]=self.table[rook_src]
     self.table[dest].moved=True
     self.table[dest].loc=Location(dest)
     self.table[rook_src]=""
     ans="O-O-O"
    # Kingside castling:
    elif horizontal==2:
     # Moves the Rook from H to F of the same row:
     rook_src="h"+self.loc[1]
     dest="f"+self.loc[1]
     self.table[dest]=self.table[rook_src]
     self.table[dest].moved=True
     self.table[dest].loc=Location(dest)
     self.table[rook_src]=""
     ans="O-O"
   # Checks:
   check="#"
   # As all kings:
   for king in self.table.kings:
    if check == "+": break
    # If enemy king:
    if king.side!=self.side:
     # If checked:
     checked=king.is_checked(record_path=True)
     if checked:
      # Has moves -> just a regular check.
      if king.moves():
       check="+"
       break
      # If doesn't have moves:
      else:
       table=self.table
       # If more than 2 pieces are attacking this King: it's over for it.
       if len(checked.by)>1:
        if check=="": check="+"
        else: check="##"
        break
       else:
        # Find the checker's attack path:
        checker=checked.by[0]
        path=checked.path[0]
        path.add(checker.loc)
        # If the attack path can be checked:
        for i in path:
         # if a piece the same side as the king can attack the path:
         m=self.is_checked(i.addr,ignore_kings=True,moving=False)
         if m and m.src != checked.src:
          print('Move block debug:',m.by[0],i.addr)
          check="+"
          break
     # If not checked:
     else:
      if check=="##": check="+"
      else: check=""
   if check == "##": check="#"
   ans+=check

   return ans
  except Exception as ex:
   # Loads backup, if needed:
   self.table.__init__(backup.board,backup.show_none,backup.update_next)
   raise ex
 def save_king(self,save_king):
  # Creates a backup of this table, modifies the table to simulate the piece moving, and see if that affects the king.
  if save_king:
   kings=[i for i in self.table.kings if i.side==self.side]
   # Doesn't care of this setting if there isn't a one true king.
   if len(kings)==1:
    king=kings[0]
    last_check=king.is_checked()
    backup=ChessBoard(self.table.board,self.table.show_none)
    # When the piece moves it has to leave its original spot. 
    # So if the original spot disappearing caused the King to be in check -> the piece can't move at all.
    self.table[self.loc]=""
    check=king.is_checked(record_path=True)
    if not last_check and check:
     if len(check.by) == 1:
      intercept=set(self.moves())&check.path[0]
      if intercept:
       self.table.__init__(backup.board,backup.show_none,backup.update_next)
       return list(intercept)
     # Restores the backup of this table:
     self.table.__init__(backup.board,backup.show_none,backup.update_next)
     return None
    # Restores the backup of this table:
    self.table.__init__(backup.board,backup.show_none,backup.update_next)
  # Piece can move, details dictated in .moves()
  return []
 def save_king_intercept(self,moves):
  kings=[i for i in self.table.kings if i.side==self.side]
  if len(kings)==1:
   king=kings[0]
   checked=king.is_checked(record_path=True)
   if checked:
    # Groups all known checked path targeted at the King:
    checked_path=set()
    for i in checked.path:
     checked_path|=i
    # Gets the moves the piece can go to that's in this checked path.
    # This is always an intercept due to how checked paths work.
    return ChessMoves(self,list(checked_path&set(moves)))
  # Returns the full moveset if there is more than 1 king, or the king is not checked at all.
  return moves
 def clone(self,data):
  self.__dict__|=data
  return self

class Pawn(ChessPiece):
 def __init__(self,table,side="w"):
  # Empties all attributes in case they're not set:
  super().__init__()
  self.side=side
  self.table=table
  self.key="P"
  self.moved=0 # 012 (not moved, moved, moved 2)
 def __repr__(self):
  return self.side+self.key
 # Finds possible moves the Pawn can make:
 def moves(self,save_king=None):
  x,y=self.loc.pos
  forward=[1,-1][self.side=="w"]
  ans=self.save_king(save_king)
  if ans is None: return ChessMoves(self,[])
  elif ans: return ChessMoves(self,ans)
  for i in range(1,3):
   mx=x+forward*i
   if -1<mx<8:
    # Moves 1 block forward:
    if i!=2:
     # can't move if blocked by any piece:
     if not self.table.board[mx][y]: ans.append((mx,y))
     # Diagonal checks:
     for d in [1,-1]:
      # Regular capture:
      my=y+d
      if -1<my<8:
       cap=self.table.board[mx][my]
       if cap:
        if cap.side != self.side: ans.append((mx,my))
       # En passant:
       elif not cap:
        cap=self.table.board[x][my]
        if cap and cap.key == "P" and cap.moved==2 and cap.side != self.side: ans.append((mx,my))
    # Moves 2 blocks forward if not yet moved, or blocked by any piece:
    elif not self.moved and not self.table.board[mx+(-1*forward)][y] and not self.table.board[mx][y]: ans.append((mx,y))
  # If king is checked and piece can intercept the attack path:
  # See if piece can intercept the attack path, if so, only allow those moves.
  ans=ChessMoves(self,ans)
  if save_king: ans=self.save_king_intercept(ans)
  return ans
   
class King(ChessPiece):
 def __init__(self,table,side="w"):
  # Empties all attributes in case they're not set:
  super().__init__()
  self.side=side
  self.table=table
  self.key="K"
  self.moved=False # used for castling rules
 def __repr__(self):
  return self.side+self.key
 # Finds possible moves the King can make:
 def moves(self,save_king=None):
  # Surrounding moves case:
  x,y=self.loc.pos
  moves=[(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
  ans=[]
  for move in moves:
   # If moved positions are valid:
   mx,my=x+move[0],y+move[1]
   if -1<mx<8 and -1<my<8 and not self.is_checked(Location((mx,my)).addr):
    target=self.table.board[mx][my]
    if target:
     if target.side != self.side: ans.append((mx,my))
    else: ans.append((mx,my))
  
  # Castling case:
  if not self.moved and not self.is_checked():
   # Left rook: (queenside)
   target=self.table.board[x][0]
   # Check tiles in king-rook path:
   if target and not target.moved:
    i=-1
    while i>-5:
     if i!=-4:
      my=y+i
      target=self.table.board[x][my]
      # If there's anything blocking the way:
      if target:
       break
      # If the 2 tiles next to king is checked:
      elif i!=-3:
       if self.is_checked(Location((x,my)).addr):
        break
     # Appends queenside castling if all break cases fail:
     else: ans.append((x,y-2))
     i-=1
   # Right rook: (kingside)
   target=self.table.board[x][7]
   # Check tiles in king-rook path:
   if target and not target.moved:
    i=1
    while i<4:
     if i!=3:
      my=y+i
      target=self.table.board[x][my]
      # If there's anything blocking the way:
      if target:
       break
      # If the 2 tiles next to king is checked:
      elif self.is_checked(Location((x,my)).addr):
       break
     # Appends queenside castling if all break cases fail:
     else: ans.append((x,y+2))
     i+=1
   
  return ChessMoves(self,ans)
class Queen(ChessPiece):
 def __init__(self,table,side="w"):
  # Empties all attributes in case they're not set:
  super().__init__()
  self.side=side
  self.table=table
  self.key="Q"
 def __repr__(self):
  return self.side+self.key
 # Finds possible moves the Queen can make:
 def moves(self,save_king=None,part=None):
  ans=self.save_king(save_king)
  if ans is None: return ChessMoves(self,[])
  elif ans: return ChessMoves(self,ans)
  # Creates a Bishop class used specifically for Bishop's moves:
  bishop_moves=Bishop(self.table,self.side).setloc(self.loc.addr).moves()
  # Creates a Rook class used specifically for Rook's moves:
  rook_moves=Rook(self.table,self.side).setloc(self.loc.addr).moves()
  if part is None:
   ans=ChessMoves(self,[])+bishop_moves+rook_moves
  elif part == "R":
   ans=ChessMoves(self,[])+rook_moves
  elif part == "B":
   ans=ChessMoves(self,[])+bishop_moves
  # If king is checked and piece can intercept the attack path:
  # See if piece can intercept the attack path, if so, only allow those moves.
  if save_king: ans=self.save_king_intercept(ans)
  return ans
class Bishop(ChessPiece):
 def __init__(self,table,side="w"):
  # Empties all attributes in case they're not set:
  super().__init__()
  self.side=side
  self.table=table
  self.key="B"
 def __repr__(self):
  return self.side+self.key
 # Finds possible moves the Bishop can make:
 def moves(self,save_king=None):
  ans=self.save_king(save_king)
  if ans is None: return ChessMoves(self,[])
  elif ans: return ChessMoves(self,ans)
  # For 2 diagonals: Gets possible moves, then only adds moves Bishop can make.
  srcpos=self.loc.pos
  # / diag:
  fd=self.table[self.loc.addr+"+"]
  val=fd.values
  ans=[]
  # Moving up:
  pos=list(srcpos)
  for i in range(fd.index-1,-1,-1):
   pos[0]-=1
   pos[1]+=1
   if val[i]:
    if self.side!=val[i].side: ans.append(tuple(pos))
    break
   else: ans.append(tuple(pos))
  # Moving down:
  pos=list(srcpos)
  for i in range(fd.index+1,len(val)):
   pos[0]+=1
   pos[1]-=1
   if val[i]:
    if self.side!=val[i].side: ans.append(tuple(pos))
    break
   else: ans.append(tuple(pos))
  # \ diag:
  bd=self.table[self.loc.addr+"-"]
  val=bd.values
  # Moving up:
  pos=list(srcpos)
  for i in range(bd.index-1,-1,-1):
   pos[0]-=1
   pos[1]-=1
   if val[i]:
    if self.side!=val[i].side: ans.append(tuple(pos))
    break
   else: ans.append(tuple(pos))
  # Moving down:
  pos=list(srcpos)
  for i in range(bd.index+1,len(val)):
   pos[0]+=1
   pos[1]+=1
   if val[i]:
    if self.side!=val[i].side: ans.append(tuple(pos))
    break
   else: ans.append(tuple(pos))
  # If king is checked and piece can intercept the attack path:
  # See if piece can intercept the attack path, if so, only allow those moves.
  ans=ChessMoves(self,ans)
  if save_king: ans=self.save_king_intercept(ans)
  return ans
class Knight(ChessPiece):
 def __init__(self,table,side="w"):
  # Empties all attributes in case they're not set:
  super().__init__()
  self.side=side
  self.table=table
  self.key="N"
 def __repr__(self):
  return self.side+self.key
 # Finds possible moves the Knight can make:
 def moves(self,save_king=None):
  try:
   ans=self.save_king(save_king)
   if ans is None: return ChessMoves(self,[])
   elif ans: return ChessMoves(self,ans)
   x,y=self.loc.pos
   moves=[(-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1)]
   ans=[]
   for move in moves:
    # If moved positions are valid:
    mx,my=x+move[0],y+move[1]
    if -1<mx<8 and -1<my<8:
     checking=self.table.board[mx][my]
     if checking:
      if checking.side != self.side: ans.append((mx,my))
     else: ans.append((mx,my))
   # If king is checked and piece can intercept the attack path:
   # See if piece can intercept the attack path, if so, only allow those moves.
   ans=ChessMoves(self,ans)
   if save_king: ans=self.save_king_intercept(ans)
   return ans
  except NameError:
   raise Exception("Can't find moves, unknown position!")
class Rook(ChessPiece):
 def __init__(self,table,side="w"):
  # Empties all attributes in case they're not set:
  super().__init__()
  self.side=side
  self.table=table
  self.key="R"
  self.moved=False
 def __repr__(self):
  return self.side+self.key
 # Finds possible moves the Rook can make:
 def moves(self,save_king=None):
  ans=self.save_king(save_king)
  if ans is None: return ChessMoves(self,[])
  elif ans: return ChessMoves(self,ans)
  tablepos=self.loc.pos
  ans=[]
  # Find all possible moves row-wise:
  for i in range(tablepos[1]+1,8):
   checking=self.table.board[tablepos[0]][i]
   if checking:
    if checking.side != self.side: ans.append((tablepos[0],i))
    break
   else: ans.append((tablepos[0],i))
  for i in range(tablepos[1]-1,-1,-1):
   checking=self.table.board[tablepos[0]][i]
   if checking:
    if checking.side != self.side: ans.append((tablepos[0],i))
    break
   else: ans.append((tablepos[0],i))
  # Find all possible moves column-wise:
  for i in range(tablepos[0]+1,8):
   checking=self.table.board[i][tablepos[1]]
   if checking:
    if checking.side != self.side: ans.append((i,tablepos[1]))
    break
   else: ans.append((i,tablepos[1]))
  for i in range(tablepos[0]-1,-1,-1):
   checking=self.table.board[i][tablepos[1]]
   if checking:
    if checking.side != self.side: ans.append((i,tablepos[1]))
    break
   else: ans.append((i,tablepos[1]))
  # If king is checked and piece can intercept the attack path:
  # See if piece can intercept the attack path, if so, only allow those moves.
  ans=ChessMoves(self,ans)
  if save_king: ans=self.save_king_intercept(ans)
  return ans

# Functions:
def ReadMove(move=''):
 movestr=move
 move=list(move)
 ans={"type":"move","action":[],"destination":"a1","source":None,"piece":"P"}
 pieces="RNBQKP"
 # Special cases:
 if move == "O-O":
  return {"type":"castling","side":"king"}
 elif move == "O-O-O":
  return {"type":"castling","side":"queen"}
 # Not a special case:
 else:
  # Rough order: check, promotion, destination, capture, source, piece
  # Check, if any:
  if move[-1] in "+#":
   if move[-1] == "#": ans["action"].append("checkmate")
   else: ans["action"].append("check")
   del move[-1]
  # Promotion, if any:
  if move[-2]=="=":
   ans["action"].append(f"promote-{move[-1]}")
   del move[-2:]
  # The next two are the tile's destination:
  ans["destination"]="".join(move[-2:])
  del move[-2:]
  # If there's more information after this:
  if move:
   # Captures:
   if move[-1]=="x":
    ans["action"].append("capture")
    del move[-1]
   if move:
    # Same piece case:
    if move[-1] in "12345678":
     ans["source"]="".join(move[-2:])
     del move[-2:]
    elif move[-1] in "abcdefgh":
     ans["source"]=move[-1]
     del move[-1]
    if move:
     # Piece information:
     if move[-1] in pieces:
      ans["piece"]=move[-1]
      del move[-1]
     # Raise exception if there's still more data (there shouldn't be):
     if move:
      move="".join(move)
      raise Exception(f"More data exists!\nUnprocessed values:'{move}'\nNeeds processing for '{movestr}'")
  return ans

# Converts a 2 letter string into a Chess Piece:
def NewPiece(data,table=None,show_none=None):
 pieces=(Rook,Knight,Bishop,Queen,King,Pawn)
 if not data or data == "--":
  return ChessPiece(show_none=show_none)
 elif isinstance(data,str):
  try:
   side,piece=data[0],data[1]
   signs='RNBQKP'
   return pieces[signs.find(piece)](table,side)
  except: raise Exception("Invalid chess piece:",data)
 elif isinstance(data,pieces): 
  # Creates a new piece with all the same attributes.
  ans=type(data)(table)
  ans.clone(data.__dict__)
  return ans
 else: raise Exception('Invalid chess piece:',data)

# Evaluates final board position for side.
def evaluate(board,side):
 opponent="b"
 if side==opponent: opponent="w"
 # Gets the parameters required:
 cx=board.control(side)["control"]
 sx=board.strength(side)["strength"]
 cy=board.control(opponent)["control"]
 sy=board.strength(opponent)["strength"]
 #print(control_x,control_y,strength_x,strength_y)
 # See if this situation is favorable or not:
 return (cx-cy)+10*(sx-sy)
 
# Minimax algorithm with ab pruning for bot:
def minimax(board,a=float('-inf'),b=float('inf'),depth=1,side="w",max_="w"):
 backup=deepcopy(board)
 ans=minimax_(backup,a,b,depth,side,max_)
 print(-ans[0],ans[1])
 return ans

def minimax_(board,a,b,depth,side,max_):
 # If game over or runs out of depth:
 legal_moves=board.options(side)
 opponent="w"
 if opponent==side:opponent=="b"
 if depth<=0 or legal_moves["options"]==0:
  return evaluate(board,side),None
 legal_moves=legal_moves["moves"]
 best_move=None
 # Maximizing half:
 if side==max_:
  max_score = float('-inf')
  for piece in legal_moves:
   for move in legal_moves[piece]:
    # Runs the move:
    backup=deepcopy(board)
    board[piece]+(move.addr+"Q")
    score = minimax_(board,a,b,depth-1,opponent,max_)
    board=backup
    if score[0]>max_score:
     max_score=score[0]
     best_move=(piece,move)
    a=max(a, score[0])
    if b<=a:break
  return max_score,best_move
 # Minimizing half:
 else:
  min_score = float('inf')
  for piece in legal_moves:
   for move in legal_moves[piece]:
    # Runs the move:
    backup=deepcopy(board)
    board[piece]+(move.addr+"Q")
    score = minimax_(board,a,b,depth-1,opponent,max_)
    board=backup
    if score[0]<min_score:
     min_score=score[0]
     best_move=(piece,move)
    b=min(b, score[0])
    if b<=a:break
  return min_score,best_move

# Determines the best move for a given side given the current board state:
def best_move(board,side):
 # Gets all the moves:
 board.options()

BOARD=[
 ["bR","bN","bB","bQ","bK","bB","bN","bR"],
 ["bP","bP","bP","bP","bP","bP","bP","bP"],
 ["--","--","--","--","--","--","--","--"],
 ["--","--","--","--","--","--","--","--"],
 ["--","--","--","--","--","--","--","--"],
 ["--","--","--","--","--","--","--","--"],
 ["wP","wP","wP","wP","wP","wP","wP","wP"],
 ["wR","wN","wB","wQ","wK","wB","wN","wR"]]

BOARD="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
x=ChessBoard(BOARD)
