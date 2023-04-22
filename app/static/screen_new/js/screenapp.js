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
            last_notific: {
                operator: '',
                ticket: ''
            },
            notifiations: [],
            stat: {},

            modal: false,
            settings: !1,
            voices: [],
            voic: null,
            utterance: null,
            isselectvoice: false
        }
    },
    created() {
        this.socket = io('/queue');
        this.axios = axios
        this.get_voices()

        setTimeout(this.init(), 1000)

        this.socket.on('call_client', (data) => {
            this.notifiations.push(data)
            this.show_modal()
        });
        this.socket.on('state', (data) => {
            this.stat = data
        });
        setTimeout(this.set_voic(), 1000)
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
            var notific = this.notifiations[0]
            this.last_notific.operator = notific.operator.name
            this.last_notific.ticket = notific.ticket.prefix + notific.ticket.num
            if (this.notifiations.length > 0 && this.modal == false) {
                this.modal = true
                if (this.voic != null){
                    this.voice(notific, this.last_notific.ticket)
                }
                else {
                    setTimeout(() => {
                        this.modal = false
                        this.notifiations.shift()
                        setTimeout(() => {
                            this.show_modal()
                        }, 500)
                  }, 3000)
                }
            }
        },
        voice(notific, string) {
            this.utterance = new SpeechSynthesisUtterance(notific.operator?.duber.replace('@', string))
            this.utterance.addEventListener('end', () => {
                this.notifiations.shift()
                this.modal = false;
                setTimeout(() => {
                    this.show_modal();
                }, 500)
            })
            this.utterance.voice = this.voic;
            speechSynthesis.speak(this.utterance);
        },
        cli() {
            console.log("click")
        },
        get_voices() {
            this.voices = window.speechSynthesis.getVoices()
        },
        show_voices_select() {
            this.get_voices()
            if (!this.isselectvoice) {
                this.isselectvoice = true;
                return
            }
            this.isselectvoice = false;
        },

        set_voic() {
            for (let i = 0; i < this.voices.length; i++) {
                if (this.voices[i].name === 'Google русский') {
                    this.voic = voices[i];
                    break;
                }
            }
        }
    }
});
app.mount('#app');