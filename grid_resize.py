import tkinter

def set_gridsize_ask(ui):
    window = tkinter.Tk(className="grid settings")
    window.geometry("300x200")
    window.resizable(False, False)
    window.attributes('-topmost', True)
    window.eval('tk::PlaceWindow . center')

    text = tkinter.Label(text="RESIZE GRID", font=(None, 18))
    text.pack(pady=20,side=tkinter.TOP)

    def validate(P):
        if len(P) == 0:
            return True
        elif (len(P) == 1 or len(P) == 2) and P.isdigit():
            return True
        else:
            return False

    def get_gridsize():
        w = width.get()
        h = height.get()
        if w == "" or h == "":
            window.destroy()
            set_gridsize_ask(ui)
            return

        ui.set_gridsize((int(w), int(h)))
        window.destroy()

    vcmd = (window.register(validate), '%P')

    width = tkinter.Entry(width=5, font=(None, 14), validate="key", validatecommand=vcmd)
    width.place(x=50, y=90)
    width.focus()

    width_text = tkinter.Label(text="WIDTH", font=(None, 11))
    width_text.place(x=53, y=120)

    height = tkinter.Entry(width=5, font=(None, 14), validate="key", validatecommand=vcmd)
    height.place(x=190, y=90)
    
    height_text = tkinter.Label(text="HEIGHT", font=(None, 11))
    height_text.place(x=193, y=120)

    xtext = tkinter.Label(text="x", font=(None, 18))
    xtext.place(x=140, y=85)

    button = tkinter.Button(text="CONFIRM", width=10, height=1, bg="Gainsboro", command=get_gridsize)
    button.pack(side=tkinter.BOTTOM, pady=10)

    window.mainloop()