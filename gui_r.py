# Tkinter related classes:
import tkinter as tk
import engine as eng
import random

# Custom color class to define different colors:
class Color:
 def __init__(self,color):
  # color: list of [r,g,b] or hex string.
  if isinstance(color,list):
   self.r,self.g,self.b=(color+[0,0,0])[:3]
   self.hex_=self.to_hex()
  elif isinstance(color,str):
   if color.startswith('#'): color=color[1:]
   self.hex_=(f'#{color}000000')[:7]
   self.r,self.g,self.b=self.to_rgb()
  self.cap()
 # Adds 2 colors as a+b
 def __add__(self,b):
  if not isinstance(b,Color): b=Color(b)
  return Color([self.r+b.r,self.g+b.g,self.b+b.b]).cap()
 # The same as a+=b
 def __iadd__(self,b):
  if not isinstance(b,Color): b=Color(b)
  self.r+=b.r
  self.g+=b.g
  self.b+=b.b
  return self.cap()
 # Subtract 2 colors as a-b
 def __sub__(self,b):
  if not isinstance(b,Color): b=Color(b)
  return Color([self.r-b.r,self.g-b.g,self.b-b.b])
 # The same as a-=b
 def __isub__(self,b):
  if not isinstance(b,Color): b=Color(b)
  self.r-=b.r
  self.g-=b.g
  self.b-=b.b
  return self.cap()
 # The same as a*b (b has to be an int/float)
 def __mul__(self,b):
  return Color([self.r*b,self.g*b,self.b*b])
 # The same as a*=b (b has to be an int/float)
 def __imul__(self,b):
  self.r*=b
  self.g*=b
  self.b*=b
  return self.cap()
 # Same as a/b (b has to be a nonzero int/float)
 def __truediv__(self,b):
  if b==0: raise ZeroDivisionError("Can't divide color",self,"to 0!")
  return Color([self.r/b,self.g/b,self.b/b])
 # Same as a/=b (b has to be a nonzero int/float)
 def __itruediv__(self,b):
  if b==0: raise ZeroDivisionError("Can't divide color",self,"to 0!")
  self.r/=b
  self.g/=b
  self.b/=b
  return self.cap()
 # 2 colors are deemed the same if they have the same RGB values:
 # Accounting for floating point precision, the difference must be really small.
 def __eq__(self,b):
  if not isinstance(b,Color):b=Color(b)
  fpd=0.000001
  return abs(self.r-b.r)<=fpd and abs(self.g-b.g)<=fpd and abs(self.b-b.b)<=fpd
 def __repr__(self):
  return self.hex_
 def __str__(self):
  return self.hex_
 # Caps RGB values to 0-255, as intended:
 def cap(self):
  self.r=min(255,max(self.r,0))
  self.g=min(255,max(self.g,0))
  self.b=min(255,max(self.b,0))
  self.hex_=self.to_hex()
  return self
 def to_hex(self):
  r,g,b=[int(i) for i in (self.r, self.g, self.b)]
  return "#{:02X}{:02X}{:02X}".format(r,g,b)
 # Note: Hex to RGB should only be used if RGB colors aren't available!
 def to_rgb(self):
  hex_ = self.hex_[1:]
  return [int(hex_[i:i+2], 16) for i in (0,2,4)]
 def mix(self,b,br=0.5):
  # Assuming self as color A.
  # b: Color B
  # br: Ratio of color B, defaults to 0.5 for an average.
  ar=1-br
  if not isinstance(b,Color): b=Color(b)
  return self*ar+b*br
 # Due to floating point precision, mix and unmix doesn't return the original color. It's close though.
 def unmix(self,b,br=0.5):
  # Assuming self as the mixed color.
  # b: Color B
  # br: Ratio of color B, defaults to 0.5 for an average.
  ar=1-br
  if not isinstance(b,Color): b=Color(b)
  return (self-b*br)/ar

class App(tk.Tk):
 def __init__(self,title):
  super().__init__()
  self.title(title)
  self.configure(bg="brown")
  # Creates the master frame for the app:
  master=FrameMaster(self)

# Master frame for the app.
class FrameMaster(tk.Frame):
 def __init__(self,holder):
  super().__init__(holder,borderwidth=3,relief="solid")
  self.V_holder=holder
  self.pack(pady=8,padx=8,fill=tk.BOTH,expand=True)
  # Makes sure the frame scales up properly:
  self.rowconfigure(0, weight=1)
  self.columnconfigure(0, weight=1)
  # Additional attributes for master frame:
  self.V_settings=FrameSettings(self,1,0)
  self.V_board=FrameBoard(self,eng.ChessBoard("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"),0,0)
  self.V_moves=FrameMoves(self,0,1)
  self.V_round=FrameRound(self,1,1)

# Frame for the round settings: (Surrender,Undo)
class FrameRound(tk.Frame):
 def __init__(self,holder,row,col,bg="green"):
  super().__init__(holder,bg=bg,borderwidth=3,relief="solid")
  self.V_holder=holder
  self.grid(row=row,column=col,sticky='nsew')
  # Adds buttons:
  frame=tk.Frame(self,bg=bg)
  self.V_endgame=tk.Button(frame,text='End Game',command=self.D_endgame)
  self.V_undo=tk.Button(frame,text='Undo',command=self.D_undo,state='disabled')
  board=self.V_holder.V_board.V_board
  self.V_undo.V_states=[]
  # Places buttons:
  frame.pack(padx=15,pady=5,fill=tk.BOTH,expand=True)
  self.V_endgame.grid(row=0,column=0,sticky='nsew')
  self.V_undo.grid(row=0,column=2,sticky='nsew')
  frame.rowconfigure(0, weight=1,uniform='row')
  frame.columnconfigure(0, weight=1,uniform='column')
  frame.columnconfigure(1, weight=1,uniform='column')
  frame.columnconfigure(2, weight=1,uniform='column')
 def D_undo(self):
  # Loads all buttons to its last state:
  button=self.V_undo
  states=button.V_states
  board=self.V_holder.V_board
  # mod=1: white, mod=0: black
  # state move order: wbwbw...
  mod=len(states)%2
  side="bw"[mod]
  # Restores board to the previous state:
  print('state',states[-1][1])
  board.D_load_state(*states.pop(-1))
  # Updates who gets to move in this state:
  board.V_side.set(side)
  board.D_allow_side(auto=False)
  # Removes the last move made in moves list:
  self.V_holder.V_moves.V_table.D_drop_move_end()
  # Stops undo action if there's no moves left:
  if len(states)==0:
   button.configure(state='disabled')
  
  # If bot side: undo again.
  if side == "b":
   self.D_undo()
  
 def D_endgame(self,add_movecode=True):
  button=self.V_endgame
  master=self.V_holder
  board=master.V_board
  moves=master.V_moves.V_table
  # Disables all tiles' commands:

  board.D_clear_prestates()
  for addr in board.V_tiles:
   tile=board.V_tiles[addr]
   tile.configure(command='',state='normal')
  button.configure(state='disabled')
  self.V_undo.config(state='disabled')
  # Adds endgame movecode:
  if add_movecode:
   sideval=board.V_side.get()
   movecode=["1-0","0-1"][sideval=="w"]
   moves.D_add_move(sideval,movecode)

# Frame for the Chess board.
class FrameBoard(tk.Frame):
 def __init__(self,holder,board,row,col,bg="green"):
  super().__init__(holder,bg=bg,borderwidth=3,relief="solid")
  self.grid(row=row,column=col,sticky='nsew')
  # Links to the engine's board for chess engine shenanigans:
  self.V_board=board
  # Dictionary of all chess tiles:
  self.V_tiles={}
  # Theme for all chess tiles:
  self.V_tilethemes=holder.V_settings.V_themes.V_available[0]
  # Move side. Uses string var for later operations.
  self.V_side=tk.StringVar()
  self.V_side.set("w")
  # Other attributes:
  self.V_holder=holder # In case a query on holder is needed
  self.V_prestates=[] # List of locations with a prestate: 
  self.V_bot_moves={} # Dict of movable positions:  
  # Startup functions:
  self.D_start()
  self.D_allow_side(auto=False)
 def __iter__(self):
  return iter(self.V_tiles)
 def __getitem__(self,addr):
  return self.V_tiles[addr]
 # Starts the Chess Board based on given board data:
 def D_start(self):
  for x in range(8):
   for y,col in enumerate("abcdefgh"):
    addr=f"{col}{x+1}"
    self.V_tiles|={addr:ChessTiles(self,addr)}
 # Allows a given side to move based on Frame's current state:
 def D_allow_side(self,auto=False,end_movecode=True):
  # Gets the side for future use:
  has_moves=False
  frame_side=self.V_side.get()
  bot_moves=self.V_bot_moves
  # Gets all possible bot moves if bot side:
  if frame_side in "b":
   bot_moves={}
   for addr in self:
    tile=self[addr]
    tile_piece=tile.V_piece
    if tile_piece.side==frame_side:
     all_moves=tile_piece.moves(save_king=True)
     if all_moves: 
      bot_moves|={addr:all_moves}
   # Once all bot moves are acquired:
   if auto and bot_moves:
    # Bot code to limit moves here
    
    # Randomly picks a move from the pool:
    move_src=random.choice(list(bot_moves.keys()))
    move=random.choice(bot_moves[move_src])
    promote=random.choice(list("QRNB"))
    self.D_move_tile(self[move_src],self[move.addr],promote)
    return None
  for addr in self:
   tile=self[addr]
   tile_config={}
   # Saves the piece at location for future use:
   tile_piece=tile.V_piece
   if tile_piece.side==frame_side:
    tile_config['state']='normal'
    if tile_piece.moves(save_king=True):
     has_moves=True
     tile_config['command']=tile.D_show_moves
    else: tile_config['command']=self.D_clear_prestates
   else:
    tile_config['state']='disabled'
   tile.configure(**tile_config)
  # If no moves are left, this is either a Checkmate or a Stalemate.
  if not has_moves:
   movesboard=self.V_holder.V_moves.V_table
   sideval=self.V_side.get()
   if movesboard.V_moves[-1][-1]=="#":
    movecode=["1-0","0-1"][sideval=="w"]
   else: movecode='1/2-1/2'
   movesboard.D_add_move(sideval,movecode)
   self.V_holder.V_round.D_endgame(add_movecode=False)
 # Removes all prestates of buttons:
 def D_clear_prestates(self):
  for addr in self.V_prestates:
   self[addr].D_remove_prestates()
  self.V_prestates=[]
 # Moves a tile from source to target:
 def D_move_tile(self,source,target,promote=None):
  # Removes all tile prestates prior to moving the tile:
  self.D_clear_prestates()
  board = self.V_board
  piece = str(source.V_piece)
  
  # Special move3: promotion
  if target.V_loc.addr[1] == '8' and piece == 'wP' or target.V_loc.addr[1] == '1' and piece == 'bP':
   side = self.V_side.get()
   if promote is None:
    buttons=self.V_tiles
    for addr in buttons:
     buttons[addr].configure(state='disabled')
    # Create the choosing menu
    promo_pieces = [side+'Q',side+'N',side+'R',side+'B']
    if piece == 'wP':
      chosing_square = [target.V_loc.addr[0]+str(int(target.V_loc.addr[1])-i) for i in range(4)]
    else:chosing_square = [target.V_loc.addr[0]+str(int(target.V_loc.addr[1])+i) for i in range(4)]
    for addr in chosing_square:
      tile = self.V_tiles[addr]
      if target.V_loc.addr != addr:
        tile.V_prestate={'bg':tile.V_color,'command':tile.cget('command'),'state':tile.cget('state')}
      else:tile.V_prestate={'bg':tile.V_color,'command':tile.D_show_moves}
      self.V_prestates.append(addr)
      tile.V_img=tk.PhotoImage(file=f'pieces/{promo_pieces[chosing_square.index(addr)]}.png')
      tile.configure(bg=tile.V_color.mix("#FFFFFF",1),image=tile.V_img,state = 'normal',command=lambda tar=target,src=source,pie=promo_pieces[chosing_square.index(addr)] :self.D_promotion(tar,src,pie))
   else: 
    self.D_promotion(target,source,side+promote)
  
  # Other moves
  else: 
    undo_button=self.V_holder.V_round.V_undo
    states=undo_button.V_states
    # Saves chessboard at the current state:
    states.append(([[eng.NewPiece(i,board,board.show_none) for i in row] for row in board.board],[i for i in board.update_next]))
    if len(states)>0:undo_button.configure(state='normal')

    movecode = self.V_board[source.V_loc]+target.V_loc.addr
    
    #print(movecode)
    #print(self.V_board)

    # Special moves1: en passant
    if target.V_loc.addr[0] != source.V_loc.addr[0] and str(target.V_piece) == '--' and piece[1] == 'P' :
      if self.V_side.get() == 'w': r = -1
      else: r = 1
      eat_addr = target.V_loc.addr[0]+str(int(target.V_loc.addr[1])+r)
      self.V_tiles[eat_addr].V_piece = target.V_piece
      self.V_tiles[eat_addr].V_img = None
      self.V_tiles[eat_addr].config(image = '')

    # Move piece
    target.V_piece=self.V_board[target.V_loc]
    source.V_piece=self.V_board[source.V_loc]
    
    target.V_img=source.V_img
    source.V_img=None

    self.V_tiles[target.V_loc.addr].config(image = target.V_img)
    self.V_tiles[source.V_loc.addr].config(image = '')
    
    # Special move2: O-O-O and O-O  
    if movecode.startswith('O-O') or movecode.startswith('O-O-O'):
      if movecode.startswith('O-O'):
        rook_addr = 'h' + target.V_loc.addr[1]
        des = 'f' + target.V_loc.addr[1]
      else:
        rook_addr = 'a' + target.V_loc.addr[1]
        des = 'd' + target.V_loc.addr[1]
      self.V_tiles[des].V_piece=self.V_board[des]
      self.V_tiles[rook_addr].V_piece=self.V_board[rook_addr]
      
      self.V_tiles[des].V_img=self.V_tiles[rook_addr].V_img
      self.V_tiles[rook_addr].V_img=None

      self.V_tiles[des].config(image = self.V_tiles[des].V_img)
      self.V_tiles[rook_addr].config(image = '')

    # Changes who's moving next:
    side=self.V_side
    movesboard=self.V_holder.V_moves.V_table
    sideval=side.get()
    movesboard.D_add_move(sideval,movecode)
    if sideval=="w": side.set("b")
    else: side.set("w")
    self.D_allow_side(auto=True)

 def D_promotion(self,target,source,piece):
  board = self.V_board
  undo_button=self.V_holder.V_round.V_undo
  states=undo_button.V_states
  # Saves chessboard at the current state:
  states.append([[eng.NewPiece(i,board,board.show_none) for i in row] for row in board.board])
  if len(states)>0:undo_button.configure(state='normal')
    
  # Moving piece
  target.V_img=tk.PhotoImage(file=f'pieces/{piece}.png')
  source.V_img=None
  self.V_tiles[target.V_loc.addr].config(image=target.V_img)
  self.V_tiles[source.V_loc.addr].config(image = '')
  movecode = self.V_board[source.V_loc]+(target.V_loc.addr+piece[1])
  target.V_piece=self.V_board[target.V_loc]
  source.V_piece=self.V_board[source.V_loc]

  # Clear the choosing menu
  if self.V_side.get() == 'w':
   chosing_square = [target.V_loc.addr[0]+str(int(target.V_loc.addr[1])-i) for i in range(1,4)]
  else:chosing_square = [target.V_loc.addr[0]+str(int(target.V_loc.addr[1])+i) for i in range(1,4)] 
  for address in chosing_square:
   tile2 = self.V_tiles[address]
   orgp=str(tile2.V_piece)
   if orgp != '--':
    tile2.V_img=tk.PhotoImage(file=f'pieces/{orgp}.png')
    tile2.config(image=tile2.V_img)
   else:
    tile2.V_img=None
    tile2.config(image='')
   self.D_clear_prestates()
  
  # Change side
  side=self.V_side
  movesboard=self.V_holder.V_moves.V_table
  sideval=side.get()
  movesboard.D_add_move(sideval,movecode)
  if sideval=="w": side.set("b")
  else: side.set("w")
  
  self.D_allow_side(auto=True)

 # Refreshes all tiles depending on its theme:
 def D_refresh_tiles(self):
  self.D_clear_prestates()
  for addr in self.V_tiles:
   tile=self.V_tiles[addr]
   color=self.V_tilethemes[("abcdefgh".find(addr[0])+int(addr[1]))%2]
   tile.configure(bg=color,activebackground=color.mix("000000",0.2))
   tile.V_color=color

 # Loads the board to a state set by engine's chessboard:
 def D_load_state(self,state,update_next=[]):
  self.D_clear_prestates()
  self.V_board.__init__(state,update_next=update_next)
  print('update_next',self.V_board.update_next)
  for addr in self.V_tiles:
   tile=self.V_tiles[addr]
   tile.__init__(self,addr)
   
# Frame for the Chess Moves List.
class FrameMoves(tk.Frame):
 def __init__(self,holder,row,col,bg="red"):
  super().__init__(holder,bg=bg,borderwidth=3,relief="solid")
  self.grid(row=row,column=col,sticky='nsew')
  self.V_holder=holder # In case a query on holder is needed
  self.dStart()
 def dStart(self):
  self.V_turn=ChessTurn(self,'w')
  self.V_table=MovesTable(self)

# Frame for the Settings section.
class FrameSettings(tk.Frame):
 def __init__(self,holder,row,col,bg="blue"):
  super().__init__(holder,bg=bg,borderwidth=3,relief="solid")
  self.grid(row=row,column=col,sticky='nsew')
  self.V_holder=holder # In case a query on holder is needed
  frame=tk.Frame(self,bg=bg)
  frame.pack(padx=15,pady=5,fill=tk.BOTH,expand=True)
  # Sets the buttons' data:
  self.V_themes=tk.Button(frame,text="Themes",command=self.D_cycle_themes)
  self.V_themes.V_available=[[Color(i) for i in x] for x in [["#EBECD0","#779556","#FFFF00","#FF0000"],["#ffdb58","#444444","#00AAFF","#ff0000"],["#f0d9b5","#8b4513","#66FF00","#8b0000"],["#f5deb3","#2e8b57","#FFAA00","#ff0000"],["#f0e68c","#483d8b","#00ff00","#ff0000"],["#e0ffff","#800000","#ff6347","#8b0000"],["#d2b48c","#556b2f","#008000","#ff4500"],["#e6e6fa","#4b0082","#8a2be2","#ff1493"],["#f8f8ff","#9932cc","#8a2be2","#ff1493"],["#ffe4b5","#228b22","#008000","#ff0000"],["#dda0dd","#a52a2a","#8b4513","#dda0dd"],["#daa520","#8b4513","#ffd700","#ff4500"],["#ffa07a","#8a2be2","#8b4513","#ff6347"],["#48d1cc","#ff6347","#ff6347","#ff0000"],["#00fa9a","#8b0000","#ff6347","#ff0000"],["#ff8c00","#9932cc","#8b4513","#ff8c00"],["#ff1493","#2f4f4f","#008000","#ff0000"],["#00ced1","#a0522d","#00ced1","#ff1493"],["#f4a460","#4169e1","#4169e1","#ff1493"],["#b8860b","#4682b4","#ff8c00","#ff6347"],["#cd853f","#8b008b","#da70d6","#8b008b"]]]
  null=tk.Frame(frame,bg=bg)
  self.V_flip=tk.Button(frame,text="Flip Board",command=self.D_flip)
  # Places the buttons and extends 
  self.V_themes.grid(row=0,column=0,sticky='nsew')
  null.grid(row=0,column=1,sticky='nsew')
  self.V_flip.grid(row=0,column=2,sticky='nsew')
  frame.rowconfigure(0, weight=1,uniform='row')
  frame.columnconfigure(0, weight=1,uniform='column')
  frame.columnconfigure(1, weight=1,uniform='column')
  frame.columnconfigure(2, weight=1,uniform='column')
 def D_cycle_themes(self):
  theme=self.V_themes
  themes=theme.V_available
  # Cycles the selected theme:
  themes.append(themes.pop(0))
  board=self.V_holder.V_board
  board.V_tilethemes=themes[0]
  board.D_refresh_tiles()
 def D_flip(self):
  board=self.V_holder.V_board
  for addr in board.V_tiles:
   tile=board.V_tiles[addr]
   info=tile.grid_info()
   x,y=info['row'],info['column']
   x=7-x
   y=7-y
   tile.grid(row=x,column=y,sticky='nsew')
  
# Information on whose turn this is:
class ChessTurn(tk.Label):
 def __init__(self,holder,start='w'):
  super().__init__(holder)
  self.V_holder=holder # In case a query on holder is needed
  # Links side data to the board's side data, and have it update the label when it's updated:
  board=self.V_holder.V_holder.V_board
  self.V_side=board.V_side
  self.V_side.trace_add('write',self.D_update_side_text)
  # Places the label on the app:
  self.configure(font=('Rockwell',24,"bold"))
  self.D_update_side_text()
  self.grid(row=0,column=0,sticky='nsew')
 def D_update_side_text(self,*args):
  theme=[Color(i) for i in ['1E1E1E','E1E1E1']]
  data=self.V_side.get()
  if data=="b":
   settings={'text':"Black's turn",'fg':theme[0],'bg':theme[1]}
  else:
   settings={'text':"White's turn",'fg':theme[1],'bg':theme[0]}
  self.configure(**settings)

# MovesTable is a frame that has 3 Listbox objects that acts like table columns.
class MovesTable(tk.Frame):
 def __init__(self,holder,bg="gray"):
  super().__init__(holder,bg=bg)
  self.V_holder=holder
  self.V_rows=0
  self.V_moves=[]
  # Creates the header row:
  self.V_whead=tk.Label(self,text="White Plays",font=('Rockwell',10,"bold"),bg=bg)
  self.V_bhead=tk.Label(self,text="Black Plays",font=('Rockwell',10,"bold"),bg=bg)
  # Creates scrollbar and 3 listboxes:
  self.V_scrollbar=tk.Scrollbar(self,orient="vertical",bg=bg)
  self.V_scrollbar.config(command=self.D_on_scroll)
  x=lambda: tk.Listbox(self,
   yscrollcommand=self.V_scrollbar.set,
   width=5,bg=bg,relief='flat',
   font=('Rockwell',12))
  self.V_rowcol,self.V_bcol,self.V_wcol=x(),x(),x()
  # Place elements in frame:
  self.V_whead.grid(row=0,column=1,sticky="nsew")
  self.V_bhead.grid(row=0,column=2,sticky="nsew")
  self.V_rowcol.grid(row=1,column=0,sticky="nsew")
  self.V_wcol.grid(row=1,column=1,sticky="nsew")
  self.V_bcol.grid(row=1,column=2,sticky="nsew")
  self.V_scrollbar.grid(row=1,column=3,sticky="ns")
  # Makes the elements scale up to match its frame:
  self.rowconfigure(1, weight=1,uniform='row')
  self.columnconfigure(1, weight=1,uniform='column')
  # Sets the frame on the app:
  self.grid(row=1,column=0,sticky="ns")
  # Makes the frame scale up to match the designated area:
  holder.rowconfigure(1, weight=1,uniform='row')
  holder.columnconfigure(0, weight=1,uniform='column')
 def D_on_scroll(self,*args):
  self.V_rowcol.yview(*args)
  self.V_bcol.yview(*args)
  self.V_wcol.yview(*args)
 def D_add_move(self,side,movecode):
  if side == "w":
   self.V_rows+=1
   self.V_rowcol.insert("end",str(self.V_rows))
   self.V_wcol.insert("end",movecode)
  else:
   self.V_bcol.insert("end",movecode)
  self.V_moves.append(movecode)
 # Deletes a move from the end of the list:
 def D_drop_move_end(self):
  # Figure out which side column is getting removed and remove from that:
  mod=len(self.V_moves)%2
  side="bw"[mod]
  if side == "w":
   self.V_rows-=1
   self.V_rowcol.delete(self.V_rows)
   self.V_wcol.delete(self.V_rows)
  if side == "b":
   self.V_bcol.delete(self.V_rows-1)
  # Removes from the overall moves list:
  self.V_moves.pop(-1)
 
# All buttons that are Chess Tiles:
class ChessTiles(tk.Button):
 def __init__(self,holder,addr):
  super().__init__(holder,borderwidth=0)
  self.V_loc=eng.Location(addr)
  self.V_holder=holder # In case a query on holder is needed
  self.V_prestate=None # Dictionary containing the state of this button before being temporarily changed.
  # Sets the tile colors based on theme:
  colors=holder.V_tilethemes
  self.V_color=colors[sum(self.V_loc.pos)%2]
  tile_config={'state':'disabled','relief':'flat','bg':self.V_color,'activebackground':self.V_color.mix("000000",0.2)}
  # Sets the tile image:
  self.V_piece=holder.V_board[addr]
  if self.V_piece:
   self.V_img=tk.PhotoImage(file=f'pieces/{self.V_piece}.png')
   tile_config['image']=self.V_img
  else: self.V_img=None
  self.configure(**tile_config)
  # Places the button:
  row,col=self.V_loc.pos
  self.grid(row=row,column=col,sticky='nsew')
  # Makes sure holder scales up as screen does:
  holder.rowconfigure(row, weight=1,uniform='row')
  holder.columnconfigure(col, weight=1,uniform='column')
 # Restores the button to its previous state: (hence removing its stored prestate)
 def D_remove_prestates(self):
  # Common function to remove all prestates from a given button.
  if self.V_prestate: self.configure(**self.V_prestate)
  # Removes its prestate from the button and the system:
  self.V_prestate=None
 # Show the moves of a piece on the board: 
 def D_show_moves(self):
  # Saves required data for later use:
  # Clicked location, button's holder, engine's board, piece at said board's location, and its moveset.
  clicked=self.V_loc
  holder=self.V_holder
  board=holder.V_board
  piece=board[clicked]
  moves=piece.moves(save_king=True)
  # Removes all prestates from holder:
  holder.D_clear_prestates()
  # As tile's valid moves:
  for loc in moves:
   tile=holder.V_tiles[loc.addr]
   # Marks these buttons as having a prestate (state before colored):
   # Also add these to FrameBoard so they can later be changed if another function is called.
   tile.V_prestate={'bg':tile.V_color,'command':tile.cget('command'),'state':tile.cget('state')}
   holder.V_prestates.append(tile.V_loc.addr)
   # Colors passable moves and applies a general function to it:
   tile.configure(
    bg=tile.V_color.mix(holder.V_tilethemes[2],0.35),
    command=lambda t=tile:holder.D_move_tile(self,t),
    state='normal')
  # Adds prestate to the tile as well as it'll be modified soon:
  self.V_prestate={'command':self.D_show_moves}
  holder.V_prestates.append(self.V_loc.addr)
  # Modifies the tile to cancel current action if it's clicked on again:
  self.configure(command=holder.D_clear_prestates)

if __name__=="__main__":
 x=App("Group 5 - AI Chess ML")
 x.mainloop()