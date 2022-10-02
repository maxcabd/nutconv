import tkinter
import sv_ttk
from io import BytesIO
from dds import read_dds, NutTexture_to_DDS, DDS_to_NutTexture, write_dds, write_png, texture_565, texture_5551, texture_4444
from tkinter import W, Menu, ttk, Grid, filedialog as fd
from utils.xfbin_lib.xfbin.structure.nut import NutTexture, Pixel_Formats
from xfbin import *
from PIL import Image, ImageTk
from brDDS import *
from utils.PyBinaryReader.binary_reader import BinaryReader
from Images import icon, Error_Texture


class App(tkinter.Tk):
    def __init__(self):
        super().__init__()

        self.title("NUT Tools GUI")
        self.geometry("1000x600")
        self.iconphoto(True, tkinter.PhotoImage(data=icon))

        # self.iconbitmap("icon.ico")
        sv_ttk.set_theme('dark')

        # window frame
        self.window = ttk.Frame(self)
        self.window.pack(fill=tkinter.BOTH, expand=True)

        # Main Window Grid Configuration
        Grid.grid_columnconfigure(self.window, index=0, weight=1)
        Grid.grid_columnconfigure(self.window, index=1, weight=1)
        Grid.grid_columnconfigure(self.window, index=2, weight=1)

        Grid.grid_rowconfigure(self.window, index=0, weight=1)
        Grid.grid_rowconfigure(self.window, index=1, weight=3)
        Grid.grid_rowconfigure(self.window, index=2, weight=1)
        Grid.grid_rowconfigure(self.window, index=3, weight=1)

        # Upper Buttons and frame
        self.upper_frame1 = ttk.Frame(
            master=self.window, width=275, height=50,)
        self.upper_frame1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.import_xfbin = ttk.Button(self.upper_frame1, text="Import XFBIN",
                                       width=10, command=self.open_xfbin)
        self.import_xfbin.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.export_xfbin = ttk.Button(self.upper_frame1, text="Export XFBIN",
                                       width=10, command=self.export_xfbin)
        self.export_xfbin.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.upper_frame2 = ttk.Frame(
            master=self.window, width=275, height=50,)
        self.upper_frame2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.import_texture = ttk.Menubutton(self.upper_frame2, text="Import Texture",
                                             width=10)
        self.import_texture.grid(
            row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.import_texture.menu = Menu(self.import_texture, tearoff=0)
        self.import_texture["menu"] = self.import_texture.menu
        self.import_texture.menu.add_command(
            label="NUT", command=self.import_texture_nut)
        self.import_texture.menu.add_command(
            label="DDS", command=self.import_texture_dds)
        self.import_texture.menu.add_command(
            label="PNG", command=self.import_texture_png)

        self.export_texture = ttk.Menubutton(self.upper_frame2, text="Export Texture",
                                             width=10)
        self.export_texture.grid(
            row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.export_texture.menu = Menu(self.export_texture, tearoff=0)
        self.export_texture['menu'] = self.export_texture.menu
        self.export_texture.menu.add_command(
            label="Export as NUT", command=self.export_nut)
        self.export_texture.menu.add_command(
            label="Export as DDS", command=self.export_dds)
        self.export_texture.menu.add_command(
            label="Export as PNG", command=self.export_png)

        # configure the grid in the upper frame
        Grid.grid_columnconfigure(self.upper_frame1, index=0, weight=1)
        Grid.grid_columnconfigure(self.upper_frame1, index=1, weight=1)
        Grid.grid_rowconfigure(self.upper_frame1, index=0, weight=1)

        Grid.grid_columnconfigure(self.upper_frame2, index=0, weight=1)
        Grid.grid_columnconfigure(self.upper_frame2, index=1, weight=1)
        Grid.grid_rowconfigure(self.upper_frame2, index=0, weight=1)
        # -----------------------------------------------------------------------------------------------------------------------

        # Xfbin and textures lists
        self.lists_frame = ttk.Frame(
            master=self.window, width=550, height=350)  # corner_radius=10,)
        self.lists_frame.grid(row=1, column=0, sticky="nsew",
                              padx=5, pady=5, columnspan=2)

        # treeview
        self.xfbin_list = ttk.Treeview(
            master=self.lists_frame, height=1, selectmode="extended")
        #self.xfbin_list.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.xfbin_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        self.xfbin_list.heading("#0", text="XFBIN Name")
        self.xfbin_list.column("#0", anchor=W, width=100)
        self.xfbin_list.bind("<<TreeviewSelect>>", self.update_texture_chunks)

        # treeview
        self.textures_list = ttk.Treeview(
            master=self.lists_frame, height=14, columns=("Count"), selectmode="extended")
        #self.textures_list.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        self.textures_list.pack(
            side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        self.textures_list.heading("#0", text="Texture Name")
        self.textures_list.column("#0", anchor='w', width=200)
        self.textures_list.heading("Count", text="Count")
        self.textures_list.column("Count", anchor='w', width=10, minwidth=10)
        self.textures_list.bind("<<TreeviewSelect>>", self.update_name_path)

        # configure the grid in the lists frame
        Grid.grid_columnconfigure(self.lists_frame, index=0, weight=1)
        Grid.grid_columnconfigure(self.lists_frame, index=1, weight=1)
        Grid.grid_rowconfigure(self.lists_frame, index=1, weight=1)
        # -----------------------------------------------------------------------------------------------------------------------

        self.texture_preview_frame = ttk.LabelFrame(
            master=self.window, width=350, height=350, text="Texture Preview")
        self.texture_preview_frame.grid(
            row=1, column=2, sticky='nsew', padx=5, pady=5)

        self.texture_preview = ttk.Label(
            master=self.texture_preview_frame, text='')
        self.texture_preview.place(relx=0.5, rely=0.49, anchor=tkinter.CENTER)

        # -----------------------------------------------------------------------------------------------------------------------

        # Texture info frame
        self.texture_info_frame = ttk.LabelFrame(
            master=self.window, width=350, height=100, text="Texture Info")
        self.texture_info_frame.grid(
            row=2, column=2, sticky='nsew', padx=5, pady=5, rowspan=2)

        # texture variables
        self.height_var = tkinter.StringVar(value="Height: ")
        self.width_var = tkinter.StringVar(value="Width: ")
        self.pixel_format_var = tkinter.StringVar(value="Pixel Format: ")
        self.mipmap_count_var = tkinter.StringVar(value="Mipmap Count: ")

        self.height_label = ttk.Label(
            master=self.texture_info_frame, textvariable=self.height_var, anchor="center")
        # update height when texture is selected
        self.height_label.grid(row=1, column=0, sticky='nsew', padx=3, pady=3)

        self.width_label = ttk.Label(
            master=self.texture_info_frame, textvariable=self.width_var, anchor="center")
        self.width_label.grid(row=1, column=1, sticky='nsew', padx=3, pady=3)

        self.pixel_format_label = ttk.Label(
            master=self.texture_info_frame, textvariable=self.pixel_format_var, anchor="center")
        self.pixel_format_label.grid(
            row=2, column=0, sticky='nsew', padx=3, pady=3)

        self.mipmap_count_label = ttk.Label(
            master=self.texture_info_frame, textvariable=self.mipmap_count_var, anchor="center")
        self.mipmap_count_label.grid(
            row=2, column=1, sticky='nsew', padx=3, pady=3)

        # configure the grid in the texture info frame
        Grid.grid_columnconfigure(self.texture_info_frame, index=0, weight=1)
        Grid.grid_columnconfigure(self.texture_info_frame, index=1, weight=1)
        Grid.grid_rowconfigure(self.texture_info_frame, index=0, weight=1)
        Grid.grid_rowconfigure(self.texture_info_frame, index=1, weight=1)
        Grid.grid_rowconfigure(self.texture_info_frame, index=2, weight=1)
        # -----------------------------------------------------------------------------------------------------------------------
        # lower buttons
        self.lower_buttons_frame1 = ttk.Frame(
            master=self.window, width=275, height=50,)
        self.lower_buttons_frame1.grid(
            row=2, column=0, sticky='nsew', padx=5, pady=5)

        self.remove_xfbin = ttk.Button(self.lower_buttons_frame1, text="Remove XFBIN",
                                       width=10, command=self.remove_xfbin)
        self.remove_xfbin.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.lower_buttons_frame2 = ttk.Frame(
            master=self.window, width=275, height=50,)
        self.lower_buttons_frame2.grid(
            row=2, column=1, sticky='nsew', padx=5, pady=5)

        self.copy_texture = ttk.Button(self.lower_buttons_frame2, text="Copy Texture",
                                       width=10, command=self.copy_nut_texture)
        self.copy_texture.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.paste_texture = ttk.Button(self.lower_buttons_frame2, text="Paste Texture",
                                        width=10, command=self.paste_nut_texture)
        self.paste_texture.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.remove_texture = ttk.Button(self.lower_buttons_frame1, text="Remove Texture",
                                         width=10, command=self.remove_texture)
        self.remove_texture.grid(
            row=0, column=1, sticky="nsew", padx=5, pady=5)

        # configure the grid in the lower buttons frame
        Grid.grid_columnconfigure(self.lower_buttons_frame1, index=0, weight=1)
        Grid.grid_columnconfigure(self.lower_buttons_frame1, index=1, weight=1)
        Grid.grid_rowconfigure(self.lower_buttons_frame1, index=0, weight=1)

        Grid.grid_columnconfigure(self.lower_buttons_frame2, index=0, weight=1)
        Grid.grid_columnconfigure(self.lower_buttons_frame2, index=1, weight=1)
        Grid.grid_rowconfigure(self.lower_buttons_frame2, index=0, weight=1)
        # -----------------------------------------------------------------------------------------------------------------------
        # Name and path frame
        self.lower_frame = ttk.Frame(master=self.window, width=550, height=50)
        self.lower_frame.grid(row=3, column=0, sticky='nsew',
                              padx=5, pady=5, columnspan=2)

        self.texture_name = ttk.Entry(master=self.lower_frame, width=15)
        self.texture_name.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.texture_name.insert(0, "Texture Name")

        self.texture_path = ttk.Entry(master=self.lower_frame, width=30)
        self.texture_path.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        self.texture_path.insert(0, "Texture Path")

        self.apply_button = ttk.Button(self.lower_frame, text="Apply",
                                       width=10, style="Accent.TButton", command=self.apply_name_path)
        self.apply_button.grid(row=0, column=2, sticky='nsew', padx=5, pady=5)

        # configure the grid in the lower frame
        Grid.grid_columnconfigure(self.lower_frame, index=0, weight=1)
        Grid.grid_columnconfigure(self.lower_frame, index=1, weight=1)
        Grid.grid_columnconfigure(self.lower_frame, index=2, weight=1)
        Grid.grid_rowconfigure(self.lower_frame, index=0, weight=1)
        # -----------------------------------------------------------------------------------------------------------------------
        # right click menus

        self.nut_menu = Menu(self.window, tearoff=0)
        self.nut_menu.add_command(
            label="Copy NUT Texture", command=self.copy_nut_texture)
        self.nut_menu.add_command(
            label="Paste NUT Texture", command=self.paste_nut_texture)
        self.nut_menu.add_command(
            label="Add Textures", command=self.add_texture)

        self.texture_menu = Menu(self.window, tearoff=0)
        self.texture_menu.add_command(
            label="Replace Texture", command=self.replace_texture)
        self.texture_menu.add_command(
            label="Remove Texture", command=self.remove_nut_texture)

        self.textures_list.bind("<Button-3>", self.show_right_click_menu)

        # -----------------------------------------------------------------------------------------------------------------------

    def open_xfbin(self):
        files = fd.askopenfilenames(
            title='Select one or more XFBINs', filetypes=[("XFBIN", "*.xfbin")])
        for file in files:
            filename = file.split("/")[-1][:-6]

            xfbin = read_xfbin(file)
            if xfbin == None:
                tkinter.messagebox.showerror("Error", "Error reading XFBIN")
            else:
                xfbins.append(xfbin)
                self.xfbin_list.insert('', tkinter.END, text=filename)

    def update_texture_chunks(self, event):
        selection = self.xfbin_list.selection()
        if len(selection) > 0:
            index = self.xfbin_list.index(selection[0])
            xfbin = xfbins[index]
            if len(self.textures_list.get_children()) > 0:
                # clear tree
                for child in self.textures_list.get_children():
                    self.textures_list.delete(child)

            self.get_texture_chunks(xfbin)

    def get_texture_chunks(self, xfbin):
        textures.clear()
        for page in xfbin.pages:
            textures.extend(page.get_chunks_by_type('nuccChunkTexture'))
        for i in range(len(textures)):
            texture: NuccChunkTexture = textures[i]
            self.textures_list.insert(
                '', tkinter.END, iid=i, text=texture.name, values=(texture.nut.texture_count))
            # insert a child
            for j in range(texture.nut.texture_count):
                self.textures_list.insert(i, 'end', text=f'Texture {j+1}')

    def remove_xfbin(self):
        selection = self.xfbin_list.selection()
        if len(selection) > 0:
            for i in selection[::-1]:
                index = self.xfbin_list.index(i)
                self.xfbin_list.delete(i)
                xfbins.pop(index)

        if len(self.textures_list.get_children()) > 0:
            # clear textures tree
            for child in self.textures_list.get_children():
                self.textures_list.delete(child)
        # clear name and path
        self.texture_name.delete(0, tkinter.END)
        self.texture_path.delete(0, tkinter.END)

    def update_name_path(self, event):
        selection = self.textures_list.selection()
        if len(selection) > 0:
            index = self.textures_list.index(selection[0])
            parent = self.textures_list.parent(selection[0])
            if parent == '':
                texture = textures[index]
                # clear current name and path
                self.texture_name.delete(0, tkinter.END)
                self.texture_path.delete(0, tkinter.END)
                # add new name and path
                self.texture_name.insert(0, texture.name)
                self.texture_path.insert(0, texture.filePath)
                # update texture preview and info
                self.update_texture_preview(texture.nut.textures[0])
                self.update_text_variables(texture.nut.textures[0].height, texture.nut.textures[0].width,
                                           texture.nut.textures[0].pixel_format, texture.nut.textures[0].mipmap_count)
            else:
                print(index)
                texture = textures[int(parent)]
                self.update_texture_preview(texture.nut.textures[int(index)])
                self.update_text_variables(texture.nut.textures[index].height, texture.nut.textures[index].width,
                                           texture.nut.textures[index].pixel_format, texture.nut.textures[index].mipmap_count)

    def update_text_variables(self, height, width, format, mipmap_count):
        self.height_var.set(f'Height: {height}')
        self.width_var.set(f'Width: {width}')
        self.pixel_format_var.set(f'Pixel Format: {Pixel_Formats.get(format)}')
        self.mipmap_count_var.set(f'Mipmaps Count: {mipmap_count}')

    def apply_name_path(self):
        active = self.textures_list.focus()
        parent = self.textures_list.parent(active)
        if parent == '':
            texture_index = self.textures_list.index(active)
            texture = textures[texture_index]

            texture.name = self.texture_name.get()
            texture.filePath = self.texture_path.get()

            self.textures_list.item(active, text=texture.name)

    def export_xfbin(self):
        active = self.xfbin_list.focus()
        if active == '':
            tkinter.messagebox.showerror(
                "Error", "No XFBIN selected to export")
        else:
            path = fd.asksaveasfilename(title='Select a location to export XFBIN',
                                        filetypes=[("XFBIN", "*.xfbin")],
                                        defaultextension=".xfbin",
                                        initialfile=f"{self.xfbin_list.item(active)['text']}.xfbin")
            if path != '':
                if len(active) > 0:
                    xfbin_index = self.xfbin_list.index(active)
                    xfbin = xfbins[xfbin_index]
                    write_xfbin(xfbin, path)
                # show message box
                tkinter.messagebox.showinfo(
                    "Export XFBIN", "XFBIN exported successfully!")

    def export_nut(self):
        texture = self.textures_list.selection()
        selection = [i for i in self.textures_list.selection(
        ) if self.textures_list.parent(i) == '']
        if len(selection) > 0:
            path = fd.askdirectory(
                title='Select a location to export the NUT texture',)
            if path != '':
                for tex in selection:
                    texture_index = self.textures_list.index(tex)
                    texture = textures[texture_index]
                    write_nut(texture, path)
            # show message box
            tkinter.messagebox.showinfo("Export NUT", "NUT exported successfully!")
        else:
            tkinter.messagebox.showerror(
                "Error", "No texture selected to export")

    def export_dds(self):
        texture = self.textures_list.selection()
        selection = [i for i in self.textures_list.selection(
        ) if self.textures_list.parent(i) == '']
        if len(selection) > 0:
            path = fd.askdirectory(
                title='Select a location to export the DDS texture')
            if path != '':
                for tex in selection:
                    texture: NuccChunkTexture = textures[self.textures_list.index(
                        tex)]
                    write_dds(texture, path)
            # show message box
            tkinter.messagebox.showinfo("Export DDS", "DDS exported successfully!")
        else:
            tkinter.messagebox.showerror(
                "Error", "No texture selected to export")

    def export_png(self):
        texture = self.textures_list.selection()
        selection = [i for i in self.textures_list.selection(
        ) if self.textures_list.parent(i) == '']
        if len(selection) > 0:
            path = fd.askdirectory(
                title='Select a location to export the PNG texture',)
            if path != '':
                for tex in selection:
                    texture: NuccChunkTexture = textures[self.textures_list.index(
                        tex)]
                    write_png(texture, path)
            # show message box
            tkinter.messagebox.showinfo("Export PNG", "PNG exported successfully!")
        else:
            tkinter.messagebox.showerror(
                "Error", "No texture selected to export")

    def copy_nut_texture(self):
        CopiedTextures.c_tex.clear()
        selection = [i for i in self.textures_list.selection()
                    if self.textures_list.parent(i) == '']
        
        if len(selection) > 0:
            for i in selection:
                index = self.textures_list.index(i)
                print(index)
                texture = textures[index]
                CopiedTextures.__init__(self, texture)
                create_texture_chunk(self)
            print(CopiedTextures.c_tex)

    def paste_nut_texture(self):
        selection = self.xfbin_list.selection()
        child_count = len(self.textures_list.get_children())
        if len(selection) > 0:
            for i, tex in enumerate(CopiedTextures.c_tex):
                textures.append(tex)
                self.textures_list.insert(
                    '', tkinter.END, iid=child_count+i, text=tex.name, values=(tex.nut.texture_count))
                for j in range(tex.nut.texture_count):
                    self.textures_list.insert(
                        child_count+i, 'end', text=f'{j}')

                # add the texture chunk to the xfbin
                index = self.xfbin_list.index(selection[0])
                xfbin = xfbins[index]
                xfbin: Xfbin
                xfbin.add_chunk_page(tex)
            print(textures)

    def remove_texture(self):
        selection = [item for item in self.textures_list.selection(
        )[::-1] if self.textures_list.parent(item) == '']
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
            image = texture_565(texture_data.texture_data,
                                texture_data.width, texture_data.height)
        elif texture_data.pixel_format == 6:
            image = texture_5551(texture_data.texture_data,
                                 texture_data.width, texture_data.height)
        elif texture_data.pixel_format == 7:
            image = texture_4444(texture_data.texture_data,
                                 texture_data.width, texture_data.height)
        else:
            dds = BytesIO(NutTexture_to_DDS(texture_data))
            try:
                image = Image.open(dds)
            except:
                ErrorTex = tkinter.PhotoImage(data=Error_Texture)
                image = Image.open('ErrorTexture.png')

        image = image.resize((370, 370), Image.Resampling.BICUBIC)

        # convert the image to a tkinter image
        image = ImageTk.PhotoImage(image)
        self.texture_preview.configure(image=image)
        self.texture_preview.image = image

    def import_texture_nut(self):
        active = self.xfbin_list.focus()
        if active == '':
            # ask the user if they want to create a new xfbin
            if tkinter.messagebox.askyesno("Import Texture", "No XFBIN is selected, would you like to create a new XFBIN?"):
                xfbin = create_xfbin()
                xfbins.append(xfbin)
                self.xfbin_list.insert(
                    '', tkinter.END, text='TempXfbin')

            else:
                return
        else:
            index = self.xfbin_list.index(active)
            xfbin = xfbins[index]
        path = fd.askopenfilename(title='Select a texture to import',
                                  filetypes=[("NUT", "*.nut")],
                                  defaultextension=".nut")

        if path != '':
            filename = path.split('/')[-1]
            texture = read_nut(path, filename)
            xfbin.add_chunk_page(texture)
            textures.append(texture)
            self.textures_list.insert(
                '', tkinter.END, text=texture.name, values=(texture.nut.texture_count))

    def import_texture_png(self):
        tkinter.messagebox.showinfo("Import Texture", "Not implemented yet")
        '''active = self.xfbin_list.focus()
        if active == '':
            #ask the user if they want to create a new xfbin
            if tkinter.messagebox.askyesno("Import Texture", "No XFBIN is selected, would you like to create a new XFBIN?"):
                xfbin = create_xfbin()
                xfbins.append(xfbin)
                self.xfbin_list.insert(
                    '', tkinter.END, text='TempXfbin')
                
            else:
                return
        else:
            index = self.xfbin_list.index(active)
            xfbin = xfbins[index]
        path = fd.askopenfilename(title='Select a texture to import',
                                filetypes=[("PNG", "*.png")],
                                defaultextension=".png")

        if path != '':
            filename = path.split('/')[-1]
            texture = read_png(path, filename)
            xfbin.add_chunk_page(texture)
            textures.append(texture)
            self.textures_list.insert(
                '', tkinter.END, text=texture.name, values=(texture.nut.texture_count))'''

    def import_texture_dds(self):
        active = self.xfbin_list.focus()
        if active == '':
            # ask the user if they want to create a new xfbin
            if tkinter.messagebox.askyesno("Import Texture", "No XFBIN is selected, would you like to create a new XFBIN?"):
                xfbin = create_xfbin()
                xfbins.append(xfbin)
                self.xfbin_list.insert(
                    '', tkinter.END, text='TempXfbin')
                # select the new xfbin
                self.xfbin_list.selection_set(
                    self.xfbin_list.get_children()[-1])
            else:
                return

        else:
            index = self.xfbin_list.index(active)
            xfbin = xfbins[index]
        path = fd.askopenfilename(title='Select a texture to import',
                                  filetypes=[("DDS", "*.dds")],
                                  defaultextension=".dds")

        if path != '':
            dds = read_dds(path)
            nuttex = DDS_to_NutTexture(dds)
            nut = Nut()
            nut.magic = b'NUT\x00'
            nut.version = 0x100
            nut.texture_count = 1
            nut.textures = [nuttex]

            texture = nut_to_texture(nut, path.split('/')[-1])
            xfbin.add_chunk_page(texture)
            textures.append(texture)
            self.textures_list.insert(
                '', tkinter.END, text=texture.name, values=(texture.nut.texture_count))

    def show_right_click_menu(self, event):
        selection = self.textures_list.selection()
        if len(selection) > 0:
            index = self.textures_list.index(selection[0])
            parent = self.textures_list.parent(selection[0])
            if parent == '':
                self.nut_menu.tk_popup(event.x_root, event.y_root)
            elif parent != '':
                self.texture_menu.tk_popup(event.x_root, event.y_root)

    def add_nut_texture(self):
        pass

    def replace_nut_texture(self):
        pass

    def remove_nut(self):
        # remove the texture from the xfbin
        selection = self.textures_list.selection()
        if len(selection) > 0:
            index = self.textures_list.index(selection[0])
            texture = textures[index]
            xfbin = xfbins[self.xfbin_list.index(
                self.xfbin_list.selection()[0])]
            xfbin.remove_chunk_page(texture)
            textures.remove(texture)
            self.textures_list.delete(selection[0])

    def add_texture(self):
        files = fd.askopenfilenames(title='Select one or more XFBINs',
                                    filetypes=[("DDS", "*.dds")], defaultextension=".dds")
        for file in files:
            if file != '':
                with open(file, 'rb') as f:
                    file = f.read()

                with BinaryReader(file, Endian.LITTLE) as br:
                    dds: BrDDS = br.read_struct(BrDDS)

                selected = self.textures_list.selection()
                index = self.textures_list.index(selected)
                texture = textures[index]
                texture.nut.texture_count += 1
                nuttex = DDS_to_NutTexture(dds)
                texture.nut.textures.append(nuttex)
                self.textures_list.insert(
                    index, 'end', text=f'Texture {len(texture.nut.textures)}')
                # update texture count
                self.textures_list.item(
                    index, values=(texture.nut.texture_count))

    def replace_texture(self):
        file = fd.askopenfilename(title='Select one or more XFBINs',
                                  filetypes=[("DDS", "*.dds")], defaultextension=".dds")
        if file != '':
            dds = read_dds(file)

            selected = self.textures_list.selection()
            parent = self.textures_list.parent(selected)
            index = self.textures_list.index(parent)
            texture = textures[index]
            texture.nut.textures[self.textures_list.index(
                selected)] = DDS_to_NutTexture(dds)
            self.update_texture_preview(
                texture.nut.textures[self.textures_list.index(selected)])
            self.update_name_path(None)
            self.update_text_variables(dds.header.height, dds.header.width, texture.nut.textures[self.textures_list.index(
                selected)].pixel_format, dds.header.mipMapCount)
        print('done')

    def remove_nut_texture(self):
        selected = self.textures_list.selection()
        for i in selected[::-1]:
            parent = self.textures_list.parent(i)
            index = self.textures_list.index(parent)
            texture = textures[index]
            texture.nut.textures.pop(self.textures_list.index(i))
            texture.nut.texture_count -= 1
            self.textures_list.delete(i)

        self.textures_list.item(index, values=(texture.nut.texture_count))
        print('done')


if __name__ == "__main__":
    app = App()
    app.mainloop()
