import os, sys
from PIL import Image

'''
========================
Does the PNG to text file operation.
'''
def do_png_to_txt(input_fn, output_fn) :
    try :
        input = Image.open(input_fn)
    except e :
        print("Invalid image file \"" + input_fn + "\".")
        sys.exit(-1)
    
    # Quickly test the return type of the pixel.
    # If it's an int, this PNG is 8-bit, which is not supported.
    if isinstance(input.getpixel((0, 0)), int) :
        print("This PNG file is 8-bit, which is not supported. Please use a 32-bit PNG.")
        sys.exit(-1)
    
    # Image size.
    size = input.size
    # List of Pikmin, for each of the five types.
    pikmin = []
    for t in xrange(5) :
        pikmin.append([])
    
    for y in xrange(size[1]) :
        for x in xrange(size[0]) :
            p = input.getpixel((x, y))
            t = -1
            if p[0] == 0 and p[1] == 0 and p[2] == 255 :
                # Blue dot means type 0.
                t = 0
            elif p[0] == 255 and p[1] == 0 and p[2] == 0 :
                # Red dot means type 1.
                t = 1
            elif p[0] == 255 and p[1] == 255 and p[2] == 0 :
                # Yellow dot means type 2.
                t = 2
            elif p[0] == 255 and p[1] == 0 and p[2] == 255 :
                # Purple dot means type 3.
                t = 3
            elif p[0] == 255 and p[1] == 255 and p[2] == 255 :
                # White dot means type 4.
                t = 4
            
            if t != -1 :
                # If this is a colored dot, add to the list of Pikmin. 0,0 is the image center.
                pikmin[t].append((x - size[0] / 2, y - size[1] / 2))
    
    output = open(output_fn, "wb")
    result_str = ""
    
    for t in xrange(5) :
        # Start by typing how many Pikmin of this type there are.
        result_str += str(len(pikmin[t])) + " "
        for p in xrange(len(pikmin[t])) :
            # Coordinates of the Pikmin. Note that in P2, less Y means down, so we have to invert.
            result_str += str(pikmin[t][p][0]) + " " + str(-pikmin[t][p][1]) + " "
    
    output.write(result_str)
    output.close()
    
    for t in xrange(5) :
        if len(pikmin[t]) > 100 :
            print(
                "WARNING: There are more than 100 " +
                ("Blue" if t == 0 else "Red" if t == 1 else "Yellow" if t == 2 else "Purple" if t == 3 else "White") +
                " Pikmin. They have all been mapped successfully, but the game is not ready to handle more than 100" +
                " of each type on the title screen. Chances are the title screen will show up corrupted in-game."
            )
    
    print(
        "Successfully mapped " + str(len(pikmin[0])) + ", " + str(len(pikmin[1])) + ", " +
        str(len(pikmin[2])) + ", " + str(len(pikmin[3])) + ", and " + str(len(pikmin[4])) +
        " Pikmin into \"" + output_fn + "\"."
    )


'''
========================
Text file to PNG.
'''
def do_txt_to_png(input_fn, output_fn) :
    try :
        input = open(input_fn, "rb")
    except e:
        print("Invalid text file \"" + input_fn + "\".")
        sys.exit(-1)
    
    # List of Pikmin, for each of the five types.
    pikmin = []
    for t in xrange(5) :
        pikmin.append([])
    # Minimum and maximum found coordinates. Used for determining image size.
    min_coords = (99999, 99999)
    max_coords = (-99999, -99999)
    
    words = input.read().split()
    cur_word = 0
    
    for t in xrange(5) :
        # Start with the word that defines how many Pikmin of this type there are.
        word = words[cur_word]
        cur_word += 1
        type_total = int(word)
        cur_point = (0, 0)
        
        for p in xrange(type_total) :
            word = words[cur_word]
            cur_word += 1
            cur_point = (float(word), cur_point[1])
            min_coords = (min(min_coords[0], cur_point[0]), min_coords[1])
            max_coords = (max(max_coords[0], cur_point[0]), max_coords[1])
            
            word = words[cur_word]
            cur_word += 1
            # Coordinates of the Pikmin. Note that in P2, less Y means down, so we have to invert.
            cur_point = (cur_point[0], -float(word))
            min_coords = (min_coords[0], min(min_coords[1], cur_point[1]))
            max_coords = (max_coords[0], max(max_coords[1], cur_point[1]))
            
            pikmin[t].append(cur_point)
    
    # Image size. Start by figuring out how much space we'll need considering the center is 0,0.
    half_width = int(max(-min_coords[0], max_coords[0]))
    half_height = int(max(-min_coords[1], max_coords[1]))
    # Add two pixels to the final size, so the pixels at the edges can have space to be put in.
    size = (half_width * 2 + 2, half_height * 2 + 2)
    
    # Adjust all Pikmin coordinates so they are drawn in the right pixel in the image.
    for t in xrange(5) :
        for p in xrange(len(pikmin[t])) :
            pikmin[t][p] = (pikmin[t][p][0] + size[0] / 2, pikmin[t][p][1] + size[1] / 2)
    
    output = Image.new("RGBA", size, (0, 0, 0, 255))
    for t in xrange(5) :
        for p in xrange(len(pikmin[t])) :
            output.putpixel(
                (int(pikmin[t][p][0]), int(pikmin[t][p][1])),
                ((0, 0, 255, 255) if t == 0 else (255, 0, 0, 255) if t == 1 else (255, 255, 0, 255) if t == 2 else
                (255, 0, 255, 255) if t == 3 else (255, 255, 255, 255))
            )
    
    output.save(output_fn)
    
    print("Successfully drew " + str(len(pikmin[0])) + ", " + str(len(pikmin[1])) + ", " + str(len(pikmin[2])) + ", " +
        str(len(pikmin[3])) + ", and " + str(len(pikmin[4])) + " Pikmin into \"" + output_fn + "\".")


'''
========================
Main function.
'''
def main() :
    if len(sys.argv) < 2 :
        print("Pikmin 2 title screen tool, by Espyo")
        print("Usage: " + sys.argv[0] + " <input file> [<output file>]")
        print("")
        print("This tool helps you create title screen Pikmin formations.")
        print("It allows you to convert an image file (PNG preferably)")
        print("into a text file that the game can understand, or the other")
        print("way around. It automatically decides which one you want based on")
        print("the file type of the input file you write.")
        print("")
        print("You might want to start with a canon, vanilla ")
        print("TXT file, like \"/user/Ebisawa/title/title.szs/logo/coordinate_eng\".")
        print("Convert that into a PNG to get an idea of what type of PNG")
        print("file this tool expects. In short: the center of the image")
        print("matches coordinates 0,0 in the title screen (roughly center-screen).")
        print("Fully red pixels (255, 0, 0) are Red Pikmin, fully yellow are")
        print("Yellow Pikmin, etc. Purples use full magenta (255, 0, 255), though.")
        print("")
        print("If you don't provide an output file, it'll be \"coordinate_eng\"")
        print("if printing to a text file, or \"map.png\" if drawing to an image file.")
        return -1
    
    input_fn = sys.argv[1]
    output_fn = ""
    png_to_txt = False
    
    if input_fn[-4:] == ".png" :
        png_to_txt = True
        output_fn = "coordinate_eng"
    else :
        output_fn = "map.png"
    
    if len(sys.argv) >= 3 :
        output_fn = sys.argv[2]
    
    if png_to_txt :
        do_png_to_txt(input_fn, output_fn)
    else :
        do_txt_to_png(input_fn, output_fn)


'''
========================
'''
if __name__=="__main__":
    main()
