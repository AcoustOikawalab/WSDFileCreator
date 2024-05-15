import math, os, tkinter as tk, tkinter.filedialog, tkinter.messagebox

def clicked_button():
    selected_options = [var.get() for var in check]
    total_checked = sum(selected_options)
    if total_checked != Ch_N:
        print("The number of channels does not match the number of checks.")
    else:
        root.destroy()

def is_available_character_determining(text): # Confirmation of character type
    for char in text:
        if not (0x20 <= ord(char) <= 0x7E):
            return False
    return True

def ASC2toHex(item, lim): # TextData input
    while True:
        user_input = input(item)     
        if len(user_input) > lim:
            print("Character limit exceeded.")
            continue  
        if not is_available_character_determining(user_input):
            print("Contains characters that cannot be used.")
            continue
        hex_values = [ord(char) & 0xFF for char in user_input]  
        if len(user_input) < lim:
            hex_values.extend([0x20] * (lim - len(user_input)))    
        return hex_values

def create_cycle(*binaries): # Making 8bit aligned unit cycle
    length=len(binaries[0])
    new_binary = []    
    for i in range(length):
        for binary in binaries: # Placing alternate data
            new_binary.append(binary[i])
    return bytes(new_binary)

file_name = input("Enter the name of the wsd file.\n")
file_name += '.wsd'

while True:
    num = input("Enter the number of channels comprising the playback data.\n")
    if num.replace('.', '').isdigit() and 1 <= float(num) < 6:
        Ch_N = math.ceil(float(num))
        break
    else:
        print("Error: The number of channels must be 1 or more and less than 6.")


print("Enter channel assignment.\n(Please refer to \"Specifications for 1-bit-coding Data File\".)")

# Ch_Asn input
# Making window
root = tk.Tk()
root.title("Channel")
options = ["Lf", "Lf-middle", "Cf", "Rf-middle", "Rf", "LFE", "Lr", "Lr-middle", "Cr", "Rr-middle", "Rr"]
check = []
 # Making checkbox
for index, option in enumerate(options):
    var = tk.IntVar()
    checkbox = tk.Checkbutton(root, text=option, variable=var)
    if index < 6:
        checkbox.grid(row=1, column=index, padx=5, pady=5, sticky="w")
    else:
        checkbox.grid(row=2, column=index-6, padx=5, pady=5, sticky="w")
    check.append(var)
btn = tk.Button(root, text="OK", command=clicked_button)
btn.grid(row=3, columnspan=5, pady=10)
root.mainloop()

check_list = [check[0].get(), check[1].get(), check[2].get(), check[3].get(), check[4].get(), check[5].get(), check[6].get(), check[7].get(), check[8].get(), check[9].get(), check[10].get()]
check_1 = [index for index, value in enumerate(check_list) if value == 1]
binaries=[]

# Loading 1bit data
for i in range(Ch_N): 
    # Making window
    root = tkinter.Tk()
    root.withdraw()
    fTyp = [("","*")]
    iDir = os.path.abspath(os.path.dirname(__file__))
    title = options[check_1[i]]
    tkinter.messagebox.showinfo('Loading 1bit data','Choose 1bit data of ' + title + '.')
    file = tkinter.filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir)
    with open(file, "rb") as binary_file:
                Stream_Data = binary_file.read()
    if i>0:
        while True:
            if len(Stream_Data) == length: 
                break
            else:
                tkinter.messagebox.showwarning('Warning', 'Selected binary data length does not match the expected length.')
    else:
        length=len(Stream_Data)
    binaries.append(Stream_Data)
    root.destroy()

if Ch_N>1:
    Stream_Data = create_cycle(*binaries)

while True:
    fs = input("Enter the frequency\n")
    try:
        fs = int(fs)
        if 40000 < fs < 2**32:
            break
        else:
            print("Error: Unsuitable value for frequency.")
    except ValueError:
        print("Error: Contains non-numeric characters.")  

General_Information = [ord(char) & 0xFF for char in '1bit'] # FileID (Fixed)
General_Information += [0] * 4 # Reserved*1
General_Information += [0X11] # Version_N (Fixed)
General_Information += [0] * 1  #Reserved*1
General_Information += [0] * 2 # Reserved*1
FileSZ = 2048 + len(Stream_Data) # File_SZ
FileSZ = FileSZ.to_bytes(8, 'big') 
General_Information += FileSZ[4:] + FileSZ[:4]
General_Information += bytes.fromhex("00000080") # TextSP (Fixed)
General_Information += bytes.fromhex("00000800") # DataSP (Fixed)
General_Information += [0] * 4 # Reserved*1

# PB_TM
tm = len(Stream_Data)*8 / fs / 3600
PB_h = int(tm)
PB_m = int(60 * (tm - PB_h))
PB_s = int(60 * (60 * (tm - PB_h) - PB_m))
Data_Spec_Information = [0, PB_s, PB_m, PB_h]
Data_Spec_Information += fs.to_bytes(4, 'big') #fs
Data_Spec_Information += [0] * 4 #Reserved*1
Data_Spec_Information += [Ch_N]#Ch_N
Data_Spec_Information += [0] * 3 #Reserved*1

#Ch_Asn binary
Ch_Asn_F = f"0{check[0].get()}{check[1].get()}{check[2].get()}{check[3].get()}{check[4].get()}0{check[5].get()}"
Data_Spec_Information += int(Ch_Asn_F, 2).to_bytes(1, 'big')#Ch_Asn_Front
Data_Spec_Information += [0] * 2 #Ch_Asn_Reversed
Ch_Asn_R = f"0{check[6].get()}{check[7].get()}{check[8].get()}{check[9].get()}{check[10].get()}00"
Data_Spec_Information += int(Ch_Asn_R, 2).to_bytes(1, 'big')#Ch_Asn_Rear

Data_Spec_Information += [0] * 12 # Reserved*1
Data_Spec_Information += [0] * 4 # Emph
Data_Spec_Information += [0] * 4 # Reserved*1
Data_Spec_Information += [0] * 16 # TimeReference
Data_Spec_Information += [0] * 40 # Reserved*1

Text_Data =  ASC2toHex("Enter Title Name. (In 128 characters or less, optional)\n",128)
Text_Data +=  ASC2toHex("Enter Composer. (In 128 characters or less, optional)\n",128)
Text_Data +=  ASC2toHex("Enter Song Writer. (In 128 characters or less, optional)\n",128)
Text_Data +=  ASC2toHex("Enter Artist Name. (In 128 characters or less, optional)\n",128)
Text_Data +=  ASC2toHex("Enter Album Name. (In 128 characters or less, optional)\n",128)
Text_Data +=  ASC2toHex("Enter Genre. (In 32 characters or less, optional)\n",32)
Text_Data +=  ASC2toHex("Enter Data & Time. (yyyyMMddhhmmss, optional)\n",32)
Text_Data +=  ASC2toHex("Enter Location. (In 32 characters or less, optional)\n",32)
Text_Data +=  ASC2toHex("Enter Comment. (In 512 characters or less, optional)\n",512)
Text_Data +=  ASC2toHex("Enter User Specific. (In 512 characters or less, optional)\n",512)
Text_Data += [0x20]*160

file_data = bytes(General_Information + Data_Spec_Information + Text_Data)
file_data += Stream_Data

with open(file_name, 'wb') as binary_file:
        binary_file.write(file_data)

print(file_name +" created!" )