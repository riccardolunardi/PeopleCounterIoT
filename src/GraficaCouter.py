from tkinter import Canvas, Message, Tk, CENTER
import random

root = Tk()
root.geometry("600x300")
root['bg']='green'

def repeat():
    global timer
    rand = random.randint(1, 15)
    # configuring the tag, to overcome over writing of text.
    cv.itemconfigure('rand', text=str(rand))
    # asking to repeat it, you can change the interval.
    timer = root.after(1000, repeat)
    if rand >= 10:
        cv.config(bg="red")
        msg.config(bg="red")
        root['bg']='red'
    else:
        cv.config(bg="green")
        msg.config(bg="green")
        root['bg']='green'

 
def stop():
    root.after_cancel(timer)

def findXCenter(canvas, item):
      coords = canvas.bbox(item)
      xOffset = (root.winfo_width() / 2) - ((coords[2] - coords[0]) / 2)
      return xOffset

cv = Canvas(root, width=1200, height=400, bg="green",highlightthickness=0)
#styles = Font(family="calibri",size=30,weight="bold")
textId = cv.create_text(600, 200, font=("Josefin Sans", 200),
               fill="white", tag='rand', justify="center")  # added a tag

msg = Message(root, text="Limite di persone = 10", width= "600", bg= "green", foreground="white", font=("Josefin Sans", 20), justify=CENTER)
msg.pack()
cv.pack()
root.attributes('-fullscreen', True)

repeat()
root.mainloop()