var ui_linear = {
    scaleDOMRect: function (R, scale) {
        R.x = R.x * scale;
        R.y = R.y * scale;
        R.width = R.width * scale;
        R.height = R.height * scale;
        return R;
    },
    vector: class {
        isInRect(R) {
            return this.x >= R.x && this.x <= R.x + R.width && this.y >= R.y && this.y <= R.y + R.height;
        }
        x;
        y;
        constructor(x, y) {
            this.x = x;
            this.y = y;
        }
        add(v) {
            return new ui_linear.vector(this.x + v.x, this.y + v.y);
        }
        subtract(v) {
            return new ui_linear.vector(this.x - v.x, this.y - v.y);
        }
        toString() {
            return "(" + Math.ceil(this.x) + "," + Math.ceil(this.y) + ")";
        }
    },
    rect: class {
        x;
        y;
        width;
        height;
        constructor(r) {
            if (r) {
                if (r instanceof DOMRect) {
                    this.x = r.x;
                    this.y = r.y;
                    this.width = r.width;
                    this.height = r.height;
                }
                if (r instanceof HTMLElement) {
                    var R = r.getBoundingClientRect();
                    this.x = R.x;
                    this.y = R.y;
                    this.width = R.width;
                    this.height = R.height;
                }
            }
        }
        expand(d) {
            this.x -= d;
            this.y -= d;
            this.width += d * 2;
            this.height += d * 2;
            return this;
        }
        isContains(v) {
            return this.x <= v.x && v.x <= this.x + this.width && this.y <= v.y && v.y <= this.y + this.height
        }
    }
}
export { ui_linear }