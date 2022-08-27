from cgitb import text
from email.mime import image
from operator import index
from select import select
import tkinter, sv_ttk, customtkinter
from turtle import width
#from pyglet import font
from io import BytesIO
from dds import nut2dds, write_dds,write_png, texture_565, texture_5551, texture_4444
from tkinter import ttk, ANCHOR, Grid, Menu, filedialog as fd
from utils.xfbin_lib.xfbin.structure.nut import NutTexture, Pixel_Formats
from xfbin import *
from PIL import Image, ImageTk



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("NUT Tools")
        self.geometry("900x500")
        self.resizable(False, False)
        self.iconbitmap("icon.ico")
        sv_ttk.set_theme('dark')

        #window frame
        self.window = ttk.Frame(self)
        self.window.pack(fill=tkinter.BOTH, expand=True)

        #Main Window Grid Configuration
        Grid.grid_columnconfigure(self.window,index=0, weight=1)
        Grid.grid_columnconfigure(self.window,index=1, weight=1)
        Grid.grid_columnconfigure(self.window,index=2, weight=1)
        Grid.grid_rowconfigure(self.window,index=0, weight=1)
        Grid.grid_rowconfigure(self.window,index=1, weight=3)
        Grid.grid_rowconfigure(self.window,index=2, weight=1)
        Grid.grid_rowconfigure(self.window,index=3, weight=1)

        #Upper Buttons and frame
        self.upper_frame1 = ttk.Frame(master=self.window, width=230, height=50,)
        self.upper_frame1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.import_xfbin = ttk.Button(self.upper_frame1, text="Import XFBIN",
        width= 10, command= self.open_xfbin)
        self.import_xfbin.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.export_xfbin = ttk.Button(self.upper_frame1, text="Export XFBIN",
        width= 10, command= self.export_xfbin)
        self.export_xfbin.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.upper_frame2 = ttk.Frame(master=self.window, width=230, height=50,)
        self.upper_frame2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.import_texture = ttk.Button(self.upper_frame2, text="Import Texture",
        width= 10, command= self.import_texture)
        self.import_texture.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.export_texture = ttk.Button(self.upper_frame2, text="Export Texture",
        width= 10, command= self.export_image)
        self.export_texture.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        #configure the grid in the upper frame
        Grid.grid_columnconfigure(self.upper_frame1,index=0, weight=1)
        Grid.grid_columnconfigure(self.upper_frame1,index=1, weight=1)
        Grid.grid_rowconfigure(self.upper_frame1,index=0, weight=1)
        
        Grid.grid_columnconfigure(self.upper_frame2,index=0, weight=1)
        Grid.grid_columnconfigure(self.upper_frame2,index=1, weight=1)
        Grid.grid_rowconfigure(self.upper_frame2,index=0, weight=1)
        #-----------------------------------------------------------------------------------------------------------------------
        
        #Xfbin and textures lists
        self.lists_frame = ttk.Frame(master=self.window, width=450, height=320) #corner_radius=10,)
        self.lists_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5, columnspan=2)

        #treeview
        self.xfbin_list = ttk.Treeview(master=self.lists_frame, height=1, selectmode="extended")
        self.xfbin_list.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.xfbin_list.heading("#0", text="XFBIN Name")
        self.xfbin_list.column("#0", anchor=tkinter.CENTER, width=100)
        self.xfbin_list.bind("<<TreeviewSelect>>", self.update_texture_chunks)

        #treeview
        self.textures_list = ttk.Treeview(master=self.lists_frame, height=17, columns=("Count"), selectmode="extended")
        self.textures_list.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        self.textures_list.heading("#0", text="Texture Name")
        self.textures_list.column("#0", anchor='w', width=200)
        self.textures_list.heading("Count", text="Count")
        self.textures_list.column("Count", anchor='w', width=10, minwidth=10)
        self.textures_list.bind("<<TreeviewSelect>>", self.update_name_path)
        

        #configure the grid in the lists frame
        Grid.grid_columnconfigure(self.lists_frame,index=0, weight=1)
        Grid.grid_columnconfigure(self.lists_frame,index=1, weight=1)
        Grid.grid_rowconfigure(self.lists_frame,index=1, weight=1)
        #-----------------------------------------------------------------------------------------------------------------------
        
        self.texture_preview_frame = ttk.LabelFrame(master=self.window, width=330, height=400, text="Texture Preview")
        self.texture_preview_frame.grid(row=1, column=2, sticky='nsew', padx=5, pady=5)

        self.texture_preview = ttk.Label(master=self.texture_preview_frame, text = '')
        self.texture_preview.place(relx=0.5, rely=0.49, anchor=tkinter.CENTER)

        #-----------------------------------------------------------------------------------------------------------------------
        
        #Texture info frame
        self.texture_info_frame = ttk.LabelFrame(master=self.window, width=330, height=100, text="Texture Info")
        self.texture_info_frame.grid(row=2, column=2, sticky='nsew', padx=5, pady=5, rowspan=2)
        
        #texture variables
        self.height_var = tkinter.StringVar(value="Height: ")
        self.width_var = tkinter.StringVar(value="Width: ")
        self.pixel_format_var = tkinter.StringVar(value="Pixel Format: ")
        self.mipmap_count_var = tkinter.StringVar(value="Mipmap Count: ")

        self.height_label = ttk.Label(master=self.texture_info_frame, textvariable= self.height_var, anchor="center")
        #update height when texture is selected
        self.height_label.grid(row=1, column=0, sticky='nsew', padx=3, pady=3)

        self.width_label = ttk.Label(master=self.texture_info_frame, textvariable= self.width_var, anchor="center")
        self.width_label.grid(row=1, column=1, sticky='nsew', padx=3, pady=3)

        self.pixel_format_label = ttk.Label(master=self.texture_info_frame, textvariable= self.pixel_format_var, anchor="center")
        self.pixel_format_label.grid(row=2, column=0, sticky='nsew', padx=3, pady=3)

        self.mipmap_count_label = ttk.Label(master=self.texture_info_frame, textvariable= self.mipmap_count_var, anchor="center")
        self.mipmap_count_label.grid(row=2, column=1, sticky='nsew', padx=3, pady=3)

        #configure the grid in the texture info frame
        Grid.grid_columnconfigure(self.texture_info_frame,index=0, weight=1)
        Grid.grid_columnconfigure(self.texture_info_frame,index=1, weight=1)
        Grid.grid_rowconfigure(self.texture_info_frame,index=0, weight=1)
        Grid.grid_rowconfigure(self.texture_info_frame,index=1, weight=1)
        Grid.grid_rowconfigure(self.texture_info_frame,index=2, weight=1)
        #-----------------------------------------------------------------------------------------------------------------------
        #Name and path frame
        self.lower_frame = ttk.Frame(master=self.window, width=470, height=50)
        self.lower_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=5, columnspan=2)
        
        self.texture_name = ttk.Entry(master=self.lower_frame, width=15)
        self.texture_name.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.texture_name.insert(0, "Texture Name")

        self.texture_path = ttk.Entry(master=self.lower_frame, width=30)
        self.texture_path.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        self.texture_path.insert(0, "Texture Path")

        self.apply_button = ttk.Button(self.lower_frame, text="Apply",
        width= 10, style="Accent.TButton", command= self.apply_name_path)
        self.apply_button.grid(row=0, column=2, sticky='nsew', padx=5, pady=5)

        #configure the grid in the lower frame
        Grid.grid_columnconfigure(self.lower_frame,index=0, weight=1)
        Grid.grid_columnconfigure(self.lower_frame,index=1, weight=1)
        Grid.grid_columnconfigure(self.lower_frame,index=2, weight=1)
        Grid.grid_rowconfigure(self.lower_frame,index=0, weight=1)
        #-----------------------------------------------------------------------------------------------------------------------
        
        #lower buttons
        self.lower_buttons_frame1 = ttk.Frame(master=self.window, width=230, height=50,)
        self.lower_buttons_frame1.grid(row=3, column=0, sticky='nsew', padx=5, pady=5)
        
        self.remove_xfbin = ttk.Button(self.lower_buttons_frame1, text="Remove XFBIN",
        width= 10, command= self.remove_xfbin)
        self.remove_xfbin.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.remove_texture = ttk.Button(self.lower_buttons_frame1, text="Remove Texture",
        width= 10, command= self.remove_texture)
        self.remove_texture.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.lower_buttons_frame2 = ttk.Frame(master=self.window, width=230, height=50,)
        self.lower_buttons_frame2.grid(row=3, column=1, sticky='nsew', padx=5, pady=5)

        self.copy_texture = ttk.Button(self.lower_buttons_frame2, text="Copy Texture",
        width= 10, command= self.copy_xfbin_texture)
        self.copy_texture.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.paste_texture = ttk.Button(self.lower_buttons_frame2, text="Paste Texture",
        width= 10, command= self.paste_xfbin_texture)
        self.paste_texture.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        #configure the grid in the lower buttons frame
        Grid.grid_columnconfigure(self.lower_buttons_frame1,index=0, weight=1)
        Grid.grid_columnconfigure(self.lower_buttons_frame1,index=1, weight=1)
        Grid.grid_rowconfigure(self.lower_buttons_frame1,index=0, weight=1)
        
        Grid.grid_columnconfigure(self.lower_buttons_frame2,index=0, weight=1)
        Grid.grid_columnconfigure(self.lower_buttons_frame2,index=1, weight=1)
        Grid.grid_rowconfigure(self.lower_buttons_frame2,index=0, weight=1)
        #-----------------------------------------------------------------------------------------------------------------------
    
    def open_xfbin(self):
        files = fd.askopenfilenames(title= 'Select one or more XFBINs', filetypes=[("XFBIN", "*.xfbin")])
        for file in files:
            filename = file.split("/")[-1][:-6]
            read_xfbin(file)

            self.xfbin_list.insert('',tkinter.END, text= filename)
    
    def update_texture_chunks(self, event):
        selection = self.xfbin_list.selection()
        if len(selection) > 0:
            index = self.xfbin_list.index(selection)
            xfbin = xfbins[index]
            if len(self.textures_list.get_children()) > 0:
                #clear tree
                for child in self.textures_list.get_children():
                    self.textures_list.delete(child)

            self.get_texture_chunks(xfbin)
            

    def get_texture_chunks(self, xfbin):
        textures.clear()
        for page in xfbin.pages:
            textures.extend(page.get_chunks_by_type('nuccChunkTexture'))
        for i in range(len(textures)):
            texture: NuccChunkTexture = textures[i]
            self.textures_list.insert('', tkinter.END, iid=i ,text= texture.name, values=( texture.nut.texture_count))
            #insert a child
            for j in range(texture.nut.texture_count):
                self.textures_list.insert(i, 'end', text= f'{j}')


    def remove_xfbin(self):
        selection = self.xfbin_list.selection() 
        if len(selection) > 0:
            for i in selection[::-1]:
                index = self.xfbin_list.index(i)
                self.xfbin_list.delete(i)
                xfbins.pop(index)
                
        if len(self.textures_list.get_children()) > 0:
            #clear textures tree
            for child in self.textures_list.get_children():
                self.textures_list.delete(child)
        #clear name and path
        self.texture_name.delete(0, tkinter.END)
        self.texture_path.delete(0, tkinter.END)


    def update_name_path(self, event):
        selection = self.textures_list.selection()
        if len(selection) > 0:
            index = self.textures_list.index(selection[0])
            parent = self.textures_list.parent(selection[0])
            if parent == '':
                texture = textures[index]
                #clear current name and path
                self.texture_name.delete(0, tkinter.END)
                self.texture_path.delete(0, tkinter.END)
                #add new name and path
                self.texture_name.insert(0, texture.name)
                self.texture_path.insert(0, texture.filePath)
                #update texture preview and info
                self.update_texture_preview(texture.nut.textures[0])
                self.update_text_variables(texture)
            
            else:
                print(index)
                texture = textures[int(parent)]
                self.update_texture_preview(texture.nut.textures[int(index)])
                self.update_text_variables(texture)

        
    def update_text_variables(self, texture: NuccChunkTexture):
        nuttex: NutTexture = texture.nut.textures[0]
        self.height_var.set(f'Height: {nuttex.height}')  
        self.width_var.set(f'Width: {nuttex.width}')
        self.pixel_format_var.set(f'Pixel Format: {Pixel_Formats.get(nuttex.pixel_format)}')
        self.mipmap_count_var.set(f'Mipmaps Count: {nuttex.mipmap_count}')
    
    def apply_name_path(self):
        selection = self.textures_list.selection()
        if len(selection) > 0:
            texture_index = self.textures_list.index(selection[0])
            texture = textures[texture_index]

            texture.name = self.texture_name.get()
            texture.filePath = self.texture_path.get()

            self.textures_list.delete(texture_index)
            self.textures_list.insert(texture_index, texture.name)
    
    def export_xfbin(self):
        selection = self.xfbin_list.selection()
        path = fd.asksaveasfilename(title= 'Select a location to export XFBIN',
                                    filetypes=[("XFBIN", "*.xfbin")],
                                    defaultextension=".xfbin",
                                    initialfile=f"{self.xfbin_list.item(selection)['text']}.xfbin")
        if path != '':
            if len(selection) > 0:
                xfbin_index = self.xfbin_list.index(selection[0])
                xfbin = xfbins[xfbin_index]
                write_xfbin(xfbin, path)
    
    def export_image(self):
        xfbin = self.xfbin_list.index(self.xfbin_list.selection())
        texture = self.textures_list.selection()
        if len(texture) > 0:
            texture: NuccChunkTexture = textures[self.textures_list.index(texture[0])]
            path = fd.asksaveasfilename(title= 'Select a location to export NUT',
                                    filetypes=[("NUT", "*.nut"), ("DDS", "*.dds"), ("PNG", "*.png")],
                                    defaultextension=".nut",
                                    initialfile=f"{texture.name}.nut")
            print(texture.name)

            if path.endswith(".nut"):
                write_nut(texture.nut, path)

            elif path.endswith(".dds"):
                write_dds(texture, path)
            elif path.endswith(".png"):
                write_png(texture, path)
    
    def copy_xfbin_texture(self):
        CopiedTextures.c_tex.clear()
        selection = self.textures_list.selection()
        if len(selection) > 0:
            for i in selection:
                index = self.textures_list.index(i)
                texture = textures[index]
                CopiedTextures.__init__(self, texture)
                create_texture_chunk(self)
            print(CopiedTextures.c_tex)
            

    def paste_xfbin_texture(self):
        selection = self.xfbin_list.selection()
        child_count = len(self.textures_list.get_children())
        if len(selection) > 0:
            for i, tex in enumerate(CopiedTextures.c_tex):
                textures.append(tex)
                self.textures_list.insert('', tkinter.END, iid= child_count+i, text= tex.name, values=(tex.nut.texture_count))
                for j in range(tex.nut.texture_count):
                    self.textures_list.insert(child_count+i, 'end', text= f'{j}')
                
                #add the texture chunk to the xfbin
                index = self.xfbin_list.index(selection[0])
                xfbin = xfbins[index]
                xfbin: Xfbin
                xfbin.add_chunk_page(tex)
            print(textures)
            

    def remove_texture(self):
        selection = [item for item in self.textures_list.selection()[::-1] if self.textures_list.parent(item) == '']
        xfbin = xfbins[self.xfbin_list.index(self.xfbin_list.selection()[0])]
        if len(selection) > 0:
            pop = [textures[self.textures_list.index(i)] for i in selection]

            for i, tex in zip(selection, pop):
                print(i, tex)
                self.textures_list.delete(i)
                textures.remove(tex)
                xfbin.remove_chunk_page(tex)
            self.update_texture_chunks(None)


    def update_texture_preview(self, texture):
        texture_data = texture
        if texture_data.pixel_format == 8:
            image = texture_565(texture_data.texture_data, texture_data.width, texture_data.height)
        elif texture_data.pixel_format == 6:
            image = texture_5551(texture_data.texture_data, texture_data.width, texture_data.height)
        elif texture_data.pixel_format == 7:
            image = texture_4444(texture_data.texture_data, texture_data.width, texture_data.height)
        else:
            dds = BytesIO(nut2dds(texture_data))
            try:
                image = Image.open(dds)
            except:
                image = Image.open('ErrorTexture.png')

        image = image.resize((370,370), Image.Resampling.BICUBIC)

        #convert the image to a tkinter image
        image = ImageTk.PhotoImage(image)
        self.texture_preview.configure(image=image)
        self.texture_preview.image = image
    
    def import_texture(self):
        index = self.xfbin_list.index(self.xfbin_list.selection()[0])
        xfbin = xfbins[index]
        path = fd.askopenfilename(title= 'Select a texture to import',
                                    filetypes=[("NUT", "*.nut"), ("DDS", "*.dds"), ("PNG", "*.png")],
                                    defaultextension=".nut")
        
        if path != '':
            filename = path.split('/')[-1]
            texture = texture_from_file(path, filename)
            xfbin.add_chunk_page(texture)
            textures.append(texture)
            self.textures_list.insert('', tkinter.END, text = texture.name, values=(texture.nut.texture_count))
    

if __name__ == "__main__":
    app = App()
    app.mainloop()