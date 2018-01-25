# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 13:48:35 2017

@author: g585476
"""

import numpy as np
from Tkinter import *
from PIL import Image, ImageTk
from numpy.random import choice as random_choice
import threading
import time

lock = threading.Lock()


def x(coord):
    return coord[0]

def y(coord):
    return coord[1]

def get_grid_neighbors(grid_width):
    def grid_neighbors(i):
        return [i-1,i+1,i-grid_width,i+grid_width]
    return grid_neighbors


class View(Toplevel):
    
    def __init__(self, master, grid_size):
        Toplevel.__init__(self, master)
        self.master = master
        self.md = False
        self.figures = []
        self.protocol('WM_DELETE_WINDOW', self.close_win)
        self.coord = []
        self.Largeur = 600
        self.Hauteur = 480
        self.R = 10
        self.grid_size = grid_size
        self.init_coord()
        self.text = ""
        self.Canevas = Canvas(self, width = self.Largeur, height =self.Hauteur, bg ='white')
        self.Canevas.pack(padx =5, pady =5, side = TOP)
        self.label = Label(self.Canevas, fg = 'green', font = ('Helvetica',28), textvariable = self.text, anchor = CENTER, bg = 'white')
        self.button_quit = Button(self, text ='Quitter')
        self.button_pause = Button(self, text = "Pause")
        self.button_nouvelle_partie = Button(self, text ='Nouvelle Partie')
        self.button_quit.pack(side=LEFT,padx=5,pady=5)
        self.button_nouvelle_partie.pack(side=LEFT,padx=5,pady=5)
        self.button_pause.pack(side=LEFT,padx=5,pady=5)
        
        
    def Clic(self, event):
        """ Gestion de l'événement Clic gauche sur la zone graphique """
        # position du pointeur de la souris
        
        X = event.x
        Y = event.y
        # on dessine un carré
        r = self.R
        self.Canevas.create_rectangle(X, Y, X+r, Y+r, fill = "green", outline="")
        
    def close_win(self):
        self.master.destroy()
        self.master.quit()
        

        
    def draw_grid(self, grid):
        r = self.R
        self.Canevas.delete("all")
        m = self.coord
        for i in range(self.grid_size):
            X = m[i][0]
            Y = m[i][1]
            if(grid[i]):
                fig = self.Canevas.create_rectangle(X, Y, X+r, Y+r, fill = "black", outline="")
                self.figures.append(fig)
            else:
                fig = self.Canevas.create_rectangle(X, Y, X+r, Y+r, fill = "", outline="black")
                self.figures.append(fig)
                
                
    def init_coord(self):
        nb_col = self.Largeur/self.R
        m = []
        for i in range(self.grid_size):
            X = (i%nb_col)*self.R
            Y = (i/nb_col)*self.R
            m.append((X,Y))
            
        self.coord = m
                
    def draw_win_message(self):
        txt = self.Canevas.create_text(self.Largeur/2, self.Hauteur/2, text=self.text, fill = 'green', font = ('Helvetica',28) )
        self.figures.append(txt)
        
    def draw_draw_message(self):
        txt = self.Canevas.create_text(self.Largeur/2, self.Hauteur/2, text=self.text, fill = 'red', font = ('Helvetica',28) )
        self.figures.append(txt)
        
    def delete_figures(self):
        for fig in self.figures:
            self.Canevas.delete(fig)
            
    def draw_cells(self, current_grid, next_grid):
        m = self.coord
        r = self.R
        for i in range(len(next_grid)):
            if next_grid[i] != current_grid[i]: 
                X = m[i][0]
                Y = m[i][1]
                if next_grid[i]:
                    self.Canevas.delete(self.figures[i])
                    fig = self.Canevas.create_rectangle(X, Y, X+r, Y+r, fill = "black", outline="")
                    self.figures[i] = fig
                else:
                    self.Canevas.delete(self.figures[i])
                    self.Canevas.delete(self.figures[i])
                    fig = self.Canevas.create_rectangle(X, Y, X+r, Y+r, fill = "white", outline="black")
                    self.figures[i] = fig                  


    
    def Effacer(self):
        """ Efface la zone graphique """
        self.Canevas.delete(ALL)

class Model():
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.data_grid = np.array([])
        self.indices = []
        self.callbacks = []
        self.update_display = None
        self.thread_handler = None
        self.started = False
        
    def stop(self):
        pass
  
            
    def add_callback(self, func):
        self.callbacks.append(func)
        
    def del_callback(self,func):
        self.callbacks.remove(func)
        
    def do_callbacks(self):
        for func in self.callbacks:
            func(self.data_grid)
            
    def fire_callback(self, list_fire, list_index_burn, list_index_done):
        func = self.f_callback
        func(list_fire, list_index_burn, list_index_done)
        
    def update_grid(self):
        self.do_callbacks()
        
    def init_grid(self):
        self.data_grid = []
        choices = [True, False]
        prob = [0.1,0.9]
        for i in range(self.grid_size):
            c = random_choice(choices, p=prob)
            self.data_grid.append(c)
        self.data_grid = np.array(self.data_grid)
        self.indices = np.array(range(len(self.data_grid)))
        self.do_callbacks()
        
    def insert_fire(self):
        lst = self.data_grid
        indices = [i for i in range(len(lst)) if lst[i] == 'o']
        indice = random_choice(indices)
        self.data_grid[indice] = '*'
        self.do_callbacks()
        
    def get_grid_neighbors(self, i):
        l = np.array([])
        grid_width = 60 #TODO - remove consstant value
        right_edge = (i%(grid_width) == 59)
        left_edge = (i%grid_width == 0)
        if right_edge:
            l = np.array([i-1,i-grid_width,i+grid_width,i-grid_width-1,i+grid_width-1])
            #l.extend([i-grid_width-1,i+grid_width-1])
        elif left_edge:
            l = np.array([i+1,i-grid_width,i+grid_width,i-grid_width+1,i+grid_width+1])
            #l.extend([i-grid_width+1,i+grid_width+1])
            
        else:
            l = np.array([i+1,i-1,i-grid_width,i+grid_width,i-grid_width-1,i-grid_width+1,i+grid_width-1,i+grid_width+1])
            #l.extend([i-grid_width-1,i-grid_width+1,i+grid_width-1,i+grid_width+1])
            
        return l[(l>0)*(l<len(self.data_grid))]
        
        
    def propagation(self):
        current_grid = self.data_grid
        next_grid = np.array(current_grid)
        tic = time.time()
        for i in self.indices:
            
            tic = time.time()
            neighbors = self.get_grid_neighbors(i)#=========================================
            #print "temps itération "+ str(i) + " ->"+ str(time.time() - tic)
            neighbors_colored = np.array(current_grid)[neighbors]
            
            nb_neighbors_colored = np.sum(neighbors_colored)
            next_grid[i] = (nb_neighbors_colored == 3) or (nb_neighbors_colored == 2 and current_grid[i])
            
        #print "temps boucle -> " + str(time.time() - tic)
        self.update_display(current_grid, next_grid)
        self.data_grid = next_grid
        #if not self.started :
        #self.thread_handler = threading.Timer(0.1, self.propagation)
        #self.thread_handler.daemon = True
        #self.thread_handler.start()
        #self.started = True
        
        

class Controller():
    def __init__(self,root):
        self.thread_handler = None
        self.pause_ = False
        self.model = Model(2880)
        self.view = View(root, self.model.grid_size)
        self.model.add_callback(self.view.draw_grid) #TODO - Homogeiniser les callbacks
        self.model.update_display = self.view.draw_cells
        self.view.Canevas.bind('<Button-1>', self.action_clic)
        self.view.button_nouvelle_partie.config(command=self.nouvelle_partie)
        self.view.button_pause.config(command = self.pause)
        self.view.button_quit.config(command = self.close)
        
    def pause(self):
        if self.pause_:
            lock.release()
            self.pause_ = False
        else:
            lock.acquire()
            self.pause_ = True

    def close(self):
        lock.acquire()
        self.view.md = True
        if self.thread_handler:
            self.thread_handler.cancel()
            self.thread_handler.join()
        self.view.master.destroy()
        self.view.master.quit()
        lock.release()
        
    def action_clic(self,event):
        
        if self.waiting:
            self.waiting = False
            lock.release()

        if not self.model.started:
             self.model.started = True 
             self.propagation()
     
    def propagation(self):
        lock.acquire()
        self.model.propagation()
        self.thread_handler = threading.Timer(0.2, self.propagation)
        self.thread_handler.daemon = True
        self.thread_handler.start()
        lock.release()

        
            
        
    def nouvelle_partie(self):
        self.waiting = True
        lock.acquire()
        self.view.delete_figures()
        self.model.init_grid()
        self.view.Canevas.bind('<Button-1>', self.action_clic)
        
        
        
    
if __name__ == '__main__':
# Création de la fenêtre principale
    Mafenetre = Tk()
    
    Mafenetre.title('Jeu de la vie')
    Mafenetre.withdraw()
    controller = Controller(Mafenetre)
    controller.nouvelle_partie()
    
    # Création d'un widget Canvas
    
    # La méthode bind() permet de lier un événement avec une fonction :
    # un clic gauche sur la zone graphique provoquera l'appel de la fonction utilisateur Clic()
    
    #Mafenetre.after(500, controller.model.propagation)    
    Mafenetre.mainloop()
#controller.model.thread_handler.join()

