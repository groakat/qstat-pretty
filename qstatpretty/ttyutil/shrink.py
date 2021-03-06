# -*- coding: utf-8 -*-
import math

from qstatpretty.ttyutil.unicode import unicode, ulen

def simple_value(formatter=str, factor=1, min_width=0, max_width=None, overflow=1):
    """Basic value function for scoring a column width"""

    def sv(content, width):
        content = formatter(content)

        if max_width and width > max_width:
            width = max_width

        if width < min_width:
            return 0

        return min(width, ulen(content)) * factor + math.log(width + 1) * overflow

    return sv


def simple_ellipsis(formatter=str):
    """Basic ellipsis function for scaling a cell"""

    def se(content, width):
        content = formatter(content)

        if(ulen(content) <= width):
            return content
        if width > 2:
            return content[0:width - 2] + u"…" + content[-1]

        elif width == 2:
            return content[0:2]
        else:
            return content[0:width]

    return se


def grow_table(tbl, width, tbldef, delimiters):

    column_overhead = 0
    margin = 0
    if delimiters:
        d = delimiters
        column_overhead = ulen(d['body_csep_m'])
        margin = ulen(d['body_l'] + d['body_r'])

    width = width - margin

    column_score = lambda col, fval, width: sum(fval(c, width) for c in col)
    column = lambda i: (r[i] for r in tbl[1:])

    scoresum = lambda col, width: column_score(column(col), tbldef[col]['fval'], width)

    colwidths = [0 for col in tbldef]

    nonempty_cols = lambda: sum(1 for i in colwidths if i > 0) - 1

    while sum(colwidths) + column_overhead * nonempty_cols() < width:

        scoregain = [scoresum(i, w + 1) - scoresum(i, w) if w > 0 else float('Inf') for i, w in enumerate(colwidths)]
        #print("\t".join( "{:.3f}".format(sg) for sg in scoregain))

        bestcol = scoregain.index(max(scoregain))

        colwidths[bestcol] += 1

    def format_col(i, c):
        if colwidths[i]:
            cf = tbldef[i]['ellipsis'](c, colwidths[i])
            return cf + " " * (colwidths[i] - ulen(cf))
        else:
            return ""

    def format_hdr(i, c):
        if colwidths[i]:
            cf = simple_ellipsis()(c, colwidths[i])
            return cf + " " * (colwidths[i] - ulen(cf))
        else:
            return ""

    header = [format_hdr(i, c) for i, c in enumerate(tbl[0]) if colwidths[i] > 0]
    body = [[format_col(i, c) for i, c in enumerate(row) if colwidths[i] > 0] for row in tbl[1:]]

    return [header] + body
