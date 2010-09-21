from gruffy.base import *


class SideBar(Base):
    """Side Bar Graph Class"""

    bar_spacing = None

    def draw(self):
        self.has_left_labels = True
        SideBar.__base__.draw(self)
        if not self.has_gdata:
            return
        self._draw_bars()

    def _draw_bars(self):
        dl = DrawableList()

        self.bar_spacing = self.bar_spacing or 0.9
        self.bars_width = self.graph_height / float(self.column_count)
        self.bar_width = self.bars_width * self.bar_spacing / len(self.norm_data)
        dl.append(DrawableStrokeOpacity(0.0))
        height = [0 for i in range(self.column_count)]
        length = [self.graph_left for i in range(self.column_count)]
        padding = (self.bar_width * (1 - self.bar_spacing)) / 2

        for row_index, data_row in enumerate(self.norm_data):
            dl.append(DrawableFillColor(Color(data_row['color'])))
            if type(self.transparent) is float:
                dl.append(DrawableFillOpacity(self.transparent))
            elif self.transparent is True:
                dl.append(DrawableFillOpacity(DEFAULT_TRANSPARENCY))
            for point_index, data_point in enumerate(data_row['values']):
                # Using the original calcs from the stacked bar chart
                # to get the difference between
                # part of the bart chart we wish to stack.
                temp1 = self.graph_left + (self.graph_width - \
                        data_point * self.graph_width - height[point_index])
                temp2 = self.graph_left + self.graph_width - height[point_index]
                difference = temp2 - temp1

                left_x = length[point_index] - 1
                left_y = self.graph_top + (self.bars_width * point_index) + \
                         (self.bar_width * row_index) + padding
                right_x = left_x + difference
                right_y = left_y + self.bar_width
                height[point_index] += (data_point * self.graph_width)
                dl.append(DrawableRectangle(left_x, left_y, right_x, right_y))

                # Calculate center based on bar_width and current row
                label_center = self.graph_top + \
                        (self.bars_width * point_index + self.bars_width / 2)
                self.draw_label(label_center, point_index)
        self.base_image.draw(dl)

    # Instead of base class version, draws vertical background lines and label
    def draw_line_markers(self):
        if self.hide_line_markers:
            return

        dl = DrawableList()
        dl.append(DrawableStrokeAntialias(False))

        # Draw horizontal line markers and annotate with numbers
        dl.append(DrawableFillColor(Color(self.marker_color)))
        dl.append(DrawableStrokeWidth(1))
        number_of_lines = 5

        # TODO Round maximum marker value to a round number like 100, 0.1, 0.5, etc.
        increment = self.significant(float(self.maximum_value) / number_of_lines)
        for index in range(number_of_lines + 1):
            line_diff = (self.graph_right - self.graph_left) / number_of_lines
            x = self.graph_right - (line_diff * index) - 1
            dl.append(DrawableLine(x, self.graph_bottom, x, self.graph_top))
            diff = index - number_of_lines
            marker_label = abs(diff) * increment

            if not self.hide_line_numbers:
                dl.append(DrawableFillColor(Color(self.font_color)))
                font = self.font if self.font else DEFAULT_FONT
                dl.append(DrawableFont(font, StyleType.NormalStyle, 400,
                                       StretchType.NormalStretch))
                dl.append(DrawableStrokeColor(Color('transparent')))
                marker_font_size = self.scale_fontsize(self.marker_font_size)
                dl.append(DrawablePointSize(self.marker_font_size))
                dl.append(DrawableGravity(GravityType.NorthWestGravity))
                text_width = self.calculate_width(marker_font_size,
                                                  str(marker_label))
                # TODO Center text over line
                x -= text_width / 2
                y = self.graph_bottom + (LABEL_MARGIN * 2.0)
                dl.append(DrawableText(x, y, "%.1f" % marker_label))
            dl.append(DrawableStrokeAntialias(True))
        self.base_image.draw(dl)

    def draw_label(self, y_offset, index):
        if index in self.labels and index not in self.labels_seen:
            dl = DrawableList()
            dl.append(DrawableFillColor(self.font_color))
            font = self.font if self.font else DEFAULT_FONT
            dl.append(DrawableGravity(GravityType.NorthGravity))
            dl.append(DrawableFont(font, StyleType.NormalStyle, 400,
                                   StretchType.NormalStretch))
            dl.append(DrawableStrokeColor(Color('transparent')))
            marker_font_size = self.scale_fontsize(self.marker_font_size)
            dl.append(DrawablePointSize(marker_font_size))
            font_hight = self.calculate_caps_height(self.marker_font_size)
            text_width = self.calculate_width(marker_font_size,
                                              self.labels[index])
            x = -(self.columns / 2 - self.graph_left + LABEL_MARGIN * 2.0 + \
                  text_width / 2.0)
            y = y_offset + font_hight / 2.0
            dl.append(DrawableText(x, y, self.labels[index]))
            self.labels_seen[index] = 1
            self.base_image.draw(dl)
