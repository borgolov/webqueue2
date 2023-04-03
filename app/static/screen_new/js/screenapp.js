const app = Vue.createApp({
    data() {
        return {
            socket: null,
            axios: null,

            room_id: "",
            location: "location",
            organization: "organiztion",
            device: {
                id: null,
                name: "device_name"
            },
            urls: ["/api/v1/device_settings", "http://192.168.3.249/slider_reg"],
            last_ticket: {
                num: 0,
                prefix: "",
                time: "",
                service: {
                    id: 0,
                    name: "service"
                }
            },
            notifiations: [],
            stat: {},

            modal: !1,
            settings: !1,
            voices: [],
            voic: null,
            utterance: null
        }
    },
    created() {
        this.socket = io('/queue');
        this.axios = axios

        setTimeout(this.init(), 1000)

        this.socket.on('call_client', (data) => {
            this.notifiations.push(data)
        });
        this.socket.on('state', (data) => {
            this.stat = data
        });
    },
    methods: {
        init() {
            this.axios.get(this.urls[0]).then(resp => {
                this.location = resp.data.location
                this.organization = resp.data.organization
                this.device = resp.data.device
            }).catch(error => {
                console.log(error)
            })
        },
        show_modal() {

        },
        voice() {

        },
        cli() {
            console.log("click")
        },
        get_voices() {
            this.voices = speechSynthesis.getVoices()
        }
    }
});
app.mount('#app');