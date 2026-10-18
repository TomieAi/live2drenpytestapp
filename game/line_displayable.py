import renpy.exports as renpy

# from https://lemmasoft.renai.us/forums/viewtopic.php?p=556861#p556861
class LineDisplayable(renpy.Displayable):

    def __init__(self, lines, color = "#fff", width = 30, **kwargs):
        super(LineDisplayable, self).__init__(**kwargs)
        self.lines = lines
        self.color = color
        self.width = width

    def render(self, width, height, st, at):
        render = renpy.Render(width, height)
        canvas = render.canvas()
        print(self.lines)
        for line in self.lines:
            canvas.line(self.color, line[0], line[1], width = self.width)
        return render