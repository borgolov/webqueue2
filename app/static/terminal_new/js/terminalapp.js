const app = Vue.createApp({
    data() {
        return {
            socket: null,
            axios: null,

            room_id: "",
            location: "location",
            organization: "",
            device: {
                id: null,
                name: ""
            },
            services: [],
            urls: ["/api/v1/device_settings"],
            last_ticket: {
                num: 0,
                prefix: "",
                time: "",
                service: {
                    id: 0,
                    name: "service"
                }
            }
        }
    },
    created() {
        this.socket = io('/queue');
        this.axios = axios
        this.get_voices()

        setTimeout(this.init(), 1000)

        this.socket.on('settings', (data) => {
            this.room_id = data.room_id
        });
        this.socket.on('last_ticket', (data) => {
            this.last_ticket = data.ticket
            this.print_ticket()
        });
    },
    methods: {
        init() {
            this.axios.get(this.urls[0]).then(resp => {
                this.location = resp.data.location
                this.organization = resp.data.organization
                this.device = resp.data.device
                this.services = resp.data.services
            }).catch(error => {
                console.log(error)
            })
        },
        show_modal() {
            
        },
        print_ticket() {
            axios.get("/ticket?prefix=" + this.last_ticket.prefix + "&number=" + this.last_ticket.num + "&service_name=" + this.$store.getters.get_last_ticket.service.name + "&locate_name=" + this.$store.getters.get_location + "&date_create=" + this.last_ticket.time).then(resp => {
                var options = {
                    printable: resp.data,
                    type: 'raw-html',
                    targetStyles: ['*'],
                    ignoreElements:['no-print','bc','gb']
                }
                printJS(options)
            })
        },
    }
});
app.mount('#app');