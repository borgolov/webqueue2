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
            },
            modal: false,

            stat: {},
            notifiations: [],
            voices: [],
            voic: null,
            utterance: null,
            isselectvoice: false,
            is_speak: false,
            last_notific: {
                operator: '',
                ticket: ''
            },
        }
    },
    created() {
        this.socket = io('/queue');
        this.axios = axios

        setTimeout(() => {
            this.get_voices()
            console.log("voices is done")
        }, 500)

        this.set_voic()

        setTimeout(this.init(), 1000)

        this.socket.on('settings', (data) => {
            this.room_id = data.room_id
        });
        this.socket.on('last_ticket', (data) => {
            this.last_ticket = data.ticket
            this.show_modal()
            this.print_ticket()
        });
        this.socket.on('state', (data) => {
            this.stat = data
        });
        this.socket.on('call_client', (data) => {
            this.notifiations.push(data)
            this.call()
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
        take_ticket(servicce_id) {
            this.show_voices_select()
            this.socket.emit('take_ticket', {
                service_id: servicce_id,
                room: this.room_id
            })
        },
        show_modal() {
            this.modal = true;
            setTimeout(() => {
                this.modal = false;
            }, 3000)
        },
        print_ticket() {
            axios.get("/ticket?prefix=" + this.last_ticket.prefix + "&number=" + this.last_ticket.num + "&service_name=" + this.last_ticket.service.name + "&locate_name=" + this.location + "&date_create=" + this.last_ticket.time).then(resp => {
                var options = {
                    printable: resp.data,
                    type: 'raw-html',
                    targetStyles: ['*'],
                    ignoreElements:['no-print','bc','gb']
                }
                printJS(options)
            })
        },

        voice(notific, string) {
            this.utterance = new SpeechSynthesisUtterance(notific.operator?.duber.replace('@', string))
            this.utterance.addEventListener('end', () => {
                this.notifiations.shift()
                this.is_speak = false
                setTimeout(() => {
                    this.call();
                }, 500)
            })
            this.utterance.voice = this.voic;
            speechSynthesis.speak(this.utterance);
        },

        call() {
            var notific = this.notifiations[0]
            this.last_notific.operator = notific.operator.name
            this.last_notific.ticket = notific.ticket.prefix + notific.ticket.num
            if (this.notifiations.length > 0 && this.is_speak == false) {
                if (this.voic != null){
                    this.is_speak = true
                    this.voice(notific, this.last_notific.ticket)
                }
            }
        },

        get_voices() {
            this.voices = window.speechSynthesis.getVoices()
        },

        set_voic() {
            for (let i = 0; i < this.voices.length; i++) {
                if (this.voices[i].name === 'Google русский') {
                    this.voic = this.voices[i];
                    break;
                }
            }
        },

        show_voices_select() {
            this.get_voices()
            this.set_voic()
            if (!this.isselectvoice) {
                this.isselectvoice = true;
                return
            }
            this.isselectvoice = false;
        },
    }
});
app.mount('#app');