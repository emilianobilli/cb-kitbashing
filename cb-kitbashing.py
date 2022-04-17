from PIL import Image
import tempfile
import subprocess


class PNGComposer(object):
    def __init__(self, files:list):
        self.png_files = files

        if len(self.png_files) == 0:
            raise ValueError('Argument must have almost 1 element')

    def compose(self, dst=None):
        first = self.png_files[0]
        composed = Image.open(first)
        if len(self.png_files) > 1:
            for other in self.png_files[1:]:
                image = Image.open(other)
                composed = Image.alpha_composite(composed, image)
        composed.save(dst, "PNG", subsampling=0, quality=100)


class Animation(object):
    step = 5
    def __init__(self, background:str, entity:str, y_range:list, x_range=None, loop=True):
        if entity != "":
            self.entity = Image.open(entity)
        else:
            raise ValueError("Entity is empty")
    
        if background != "":
            self.background = background
        else:
            raise ValueError("Backgound is empty")

        if y_range != [] and len(y_range) == 2:
            self.range = y_range
        else:
            raise ValueError("y_range must have 2 values")

        self.loop = loop

    def compose(self, name:str=""):
        images = []
        start, end = tuple(self.range)
        if start > end:
            self.step = self.step * -1
        
        for i in range(start,end,self.step):
            im = Image.open(self.background)
            im.paste(self.entity, (0,i), self.entity)
            images.append(im)
        
        if self.loop:
            self.step = self.step * -1
        
            for i in range(end,start,self.step):
                im = Image.open(self.background)
                im.paste(self.entity, (0,i), self.entity)
                images.append(im)

        images[0].save(name, format="GIF", save_all=True, append_images=images[1:], loop=0, disposal=2)


class GifOverlay(object):
    def __init__(self, base_video:str, overlay:list):
        self.base_video = base_video
        self.overlay = overlay

    @staticmethod
    def _video(video, overlay, output):
        command = [
            "ffmpeg",
            "-y",
            "-i",
            "%s" % video,
            "-ignore_loop",
            "0",
            "-i",
            "%s" % overlay,
            "-filter_complex",
            "\"overlay=shortest=1:format=auto\"",
            "%s" % output
        ]

        if subprocess.run(" ".join(command), shell=True).returncode == 0:
            return True
        return False

    def render(self, output):
        video_input = self.base_video
        for o in self.overlay[:-1]:  
            _, video_output = tempfile.mkstemp(suffix='.mp4')
            GifOverlay._video(video_input, o, video_output)
            video_input = video_output

        return GifOverlay._video(video_input, self.overlay[len(self.overlay)-1], output)


class CannonBall(object):
    def __init__(self, background=None, traits=[], floaties=None):
        self.background = background
        self.traits = traits
        self.floaties = floaties

    def compose(self, destination=None):
        png_output = None
        if self.traits:
            png = PNGComposer(self.traits):
            _, png_output = tempfile.mkstemp(suffix='.png')
            png.compose(png_output)

        if png_output:
            gif = Animation("base_transparent.png", png_output, [198,238])
            _, gif_output = tempfile.mkstemp(suffix='.gif')
            gif.compose(gif_output)

        gifs = [gif_output]
        if floaties:
            gifs.append(floaties)
        
        overlay = GifOverlay(self.background, gifs)
        overlat.render(destination)




if __name__ == '__main__':
    a = Animation("base1000x1000.png", "group.png", [198,238])
    a.save_gif("gif.gif")

    o = GifOverlay("Cannonball-Background-Teal.mp4", ["gif.gif", "Cannonball-Floaties-Viking-Helmet.gif"])
    o.render("out_2.mp4")