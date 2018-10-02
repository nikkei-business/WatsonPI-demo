const circle = {cx: size, cy: size, r: size*0.8}
Vue.component('polygraph', {
    props: {
        stats: Array,
        circle: Object
    },
    template: '#polygraph-template',
    computed: {
        points() {
            const stats = this.stats;
            const total = stats.length
            return stats.map((stat, i) => {
                const point = valueToPoint(stat.value, i, total);
                return point.x + ',' + point.y;
            }).join(' ');
        }
    },
    components: {
        'axis-label': {
            props: {
                stat: Object,
                index: Number,
                total: Number
            },
            template: '#axis-label-template',
            computed: {
                point() {
                    return valueToPoint(
                        +this.stat.value + 10,
                        this.index,
                        this.total
                    );
                }
            }
        }
    }
});
function valueToPoint(value, index, total) {
    const r = value * circle.r / size;
    const angle = Math.PI * 2 / total * index - Math.PI / 2;
    const tx = r * Math.cos(angle) + circle.cx;
    const ty = r * Math.sin(angle) + circle.cy;
    return {
        x: tx,
        y: ty
    };
}
const vm = new Vue({
    data: {
        newLabel: '',
        stats: stats,
        circle: circle
    },
    methods: {
        add(event) {
            event.preventDefault();
            const newLabel = this.newLabel.trim();
            this.newLabel = '';
            if (!newLabel) {return}
            this.stats.push({
                label: newLabel,
                value: 100,
                id: this.getNewId()
            })
        },
        remove(stat) {
            const stats = this.stats;
            if (stats.length > 3) {
                this.stats = stats.filter((_stat) => _stat !== stat);
            } else {
                alert(`Can't delete more!`);
            }
        },
        getNewId() {
            const ids = this.stats.map((stat) => stat.id);
            return Math.max(...ids) + 1;
        }
    }
});
document.addEventListener('DOMContentLoaded', (event) =>
    vm.$mount('#demo')
);
