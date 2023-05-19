# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 12:46:54 2021

@author: dfuggetta
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy import Config
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.graphics import *
from kivy.clock import Clock

import random as rd
import numpy as np
import matplotlib.pyplot as plt
import time

from brain_ai import Dqn

Config.set('graphics', 'multisamples', '0')

action2rotation=[-45,-20,0,20,45]
last_reward=0
scores=[]
brain=Dqn(3,5,0.9)
fixed_obstacles=[]
yes=False

class Rettangolo(Widget):
    vx=NumericProperty(2)
    vy=NumericProperty(0)
    vxy= ReferenceListProperty(vx,vy)

    def moveR(self):
        self.pos=Vector(*self.vxy)+self.pos

class AirPlane(Widget):
    velx=NumericProperty(0)
    vely=NumericProperty(4)
    velxy=ReferenceListProperty(velx,vely)
    angle=NumericProperty(0)
    rotation=NumericProperty(0)
    sensor1x=NumericProperty(0)
    sensor1y=NumericProperty(0)
    sensor1=ReferenceListProperty(sensor1x,sensor1y)
    sensor2x=NumericProperty(0)
    sensor2y=NumericProperty(0)
    sensor2=ReferenceListProperty(sensor2x,sensor2y)
    sensor3x=NumericProperty(0)
    sensor3y=NumericProperty(0)
    sensor3=ReferenceListProperty(sensor3x,sensor3y)
    signal1=NumericProperty(0)
    signal2=NumericProperty(0)
    signal3=NumericProperty(0)

    def moveA(self,rotation):
        self.rotation=rotation
        self.angle=self.angle+self.rotation
        self.velxy=Vector(*self.velxy).rotate(self.rotation)
        self.pos=Vector(*self.velxy)+self.pos
        self.sensor1=Vector(0,10).rotate(self.rotation)+self.pos
        self.sensor2=Vector(-25,-10).rotate(self.rotation)+self.pos
        self.sensor3=Vector(25,-10).rotate(self.rotation)+self.pos

class Prova2Main(Widget):
    global action2rotation
    rList=[None]*8
    airplane=ObjectProperty(0)
    vettore=None

    def setPos(self):
        vect=Vector(rd.randint(10, 20), rd.randint(450,550))
        for i in range(0,8):
            with self.canvas:
                self.rList[i]=Rettangolo()
                self.rList[i].pos= vect +self.rList[i].pos+Vector(i*100,0)

    def calCulation(self):
        global fixed_obstacles
        global yes
        self.vettore=np.zeros((self.width,self.height))
        for i in range(0,8):
            self.vettore[int(self.rList[i].x):int(self.rList[i].x)+10, int(self.rList[i].y):int(self.rList[i].y)+30]=1
        self.airplane.signal1=int(np.sum(self.vettore[int(self.airplane.sensor1x)-10:int(self.airplane.sensor1x)+10,int(self.airplane.sensor1y)-10:int(self.airplane.sensor1y)+10]))/(self.width*self.height)
        self.airplane.signal2=int(np.sum(self.vettore[int(self.airplane.sensor2x)-10:int(self.airplane.sensor2x)+10,int(self.airplane.sensor2y)-10:int(self.airplane.sensor2y)+10]))/(self.width*self.height)
        self.airplane.signal3=int(np.sum(self.vettore[int(self.airplane.sensor3x)-10:int(self.airplane.sensor3x)+10,int(self.airplane.sensor3y)-10:int(self.airplane.sensor3y)+10]))/(self.width*self.height)
        if (self.airplane.sensor1x<10) or (self.airplane.sensor1x>self.width-10) or (self.airplane.sensor1y<10) or (self.airplane.sensor1y>self.height-10):
             self.airplane.signal1=1
        
        if(yes):
           self.airplane.signal1+=int(np.sum(fixed_obstacles[int(self.airplane.sensor1x)-10:int(self.airplane.sensor1x)+10,int(self.airplane.sensor1y)-10:int(self.airplane.sensor1y)+10]))/(self.width*self.height)
           self.airplane.signal2+=int(np.sum(fixed_obstacles[int(self.airplane.sensor2x)-10:int(self.airplane.sensor2x)+10,int(self.airplane.sensor2y)-10:int(self.airplane.sensor2y)+10]))/(self.width*self.height)
           self.airplane.signal3+=int(np.sum(fixed_obstacles[int(self.airplane.sensor3x)-10:int(self.airplane.sensor3x)+10,int(self.airplane.sensor3y)-10:int(self.airplane.sensor3y)+10]))/(self.width*self.height)
           if (self.airplane.sensor1x<10) or (self.airplane.sensor1x>self.width-10) or (self.airplane.sensor1y<10) or (self.airplane.sensor1y>self.height-10):
               self.airplane.signal1=1 
            
    def update(self,dt):
        global action2rotation
        global last_reward
        global scores
        global brain
        last_signal=[self.airplane.signal1,self.airplane.signal2,self.airplane.signal3]
        action=brain.update(last_reward,last_signal)
        scores.append(brain.score())
        rotation = action2rotation[action]
        self.airplane.moveA(rotation)
        for i in range(0,8):
            self.rList[i].moveR()
        self.calCulation()
        if(self.airplane.signal1>0) or (self.airplane.signal2>0) or (self.airplane.signal3>0):
            last_reward=1
        elif(action==2):
            last_reward=0.5
        else:
            last_reward=-0.8
        
        if (self.rList[7].x>self.width):
            newr=rd.randint(10, 20)
            for i in range(0,8):
                self.rList[i].x=newr+i*100
                self.rList[i].y-=100
        if (self.rList[0].y<-140):
            self.setPos()
        if self.airplane.x<10:
            self.airplane.x=10
            last_reward = -1
        if self.airplane.x>self.width-10:
            self.airplane.x=self.width-10
            last_reward = -1
        if self.airplane.y<10:
            self.airplane.y=10
            last_reward = -1
        if self.airplane.y>self.height-10:
            self.airplane.y= self.height-10
            last_reward = -1
            

class MyPaintWidget(Widget):
    global fixed_obstacles
    global yes
    newRList=[None]*10
    
    def on_touch_down(self, touch):
        for i in range(0,10):
            with self.canvas:
                self.newRList[i]=Rettangolo()
                self.newRList[i].pos= self.newRList[i].pos+Vector(rd.randint(0, fixed_obstacles.shape[0]), rd.randint(0, fixed_obstacles.shape[1]))
            fixed_obstacles[int(self.newRList[i].x):int(self.newRList[i].x)+10, int(self.newRList[i].y):int(self.newRList[i].y)+30]
        yes=True


class Prova2App(App):
    def build(self):
        global fixed_obstacles
        prova2=Prova2Main()
        prova2.setPos()
        fixed_obstacles=np.zeros((prova2.width,prova2.height))
        Clock.schedule_interval(prova2.update, 1.0 / 60.0)
        self.painter=MyPaintWidget()
        clearbtn=Button(text = 'clear')
        savebtn = Button(text = 'save', pos = (prova2.width, 0))
        loadbtn = Button(text = 'load', pos = (2 * prova2.width, 0))
        clearbtn.bind(on_release = self.clear_canvas)
        savebtn.bind(on_release = self.save)
        loadbtn.bind(on_release = self.load)
        prova2.add_widget(self.painter)
        prova2.add_widget(clearbtn)
        prova2.add_widget(savebtn)
        prova2.add_widget(loadbtn)
        return prova2
    
    def clear_canvas(self, obj):
        global fixed_obstacles
        self.painter.canvas.clear()
        del self.painter.newRList
        fixed_obstacles=np.zeros(self.prova2.width, self.prova2.height)
        
    def save(self, obj):
        print("saving brain...")
        brain.save()
        plt.plot(scores)
        plt.show()

    def load(self, obj):
        print("loading last saved brain...")
        brain.load()

if __name__=='__main__':
    Prova2App().run()