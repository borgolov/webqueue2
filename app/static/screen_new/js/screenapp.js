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
            urls: [
                "/api/v1/device_settings", 
                "http://192.168.3.249/slider_reg", 
                "/static/screen_new/sound/screen.mp3"
            ],
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
            is_screen_sound: true,
            modal_settings: false,
            voice_settings: {
                volume: 1,
                rate: 1,
                pitch:1
            },
            audio_settings: {
                volume: 1
            }
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
            this.last_notific.operator = notific?.operator?.name
            this.last_notific.ticket = notific?.ticket.prefix + notific?.ticket.num
            if (this.notifiations.length > 0 && this.modal == false) {
                this.modal = true
                this.suound_signal(() => {
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
                })          
            }
        },
        voice(notific, string) {
            this.utterance = new SpeechSynthesisUtterance(notific?.operator?.duber.replace('@', string))
            this.utterance.addEventListener('end', () => {
                this.notifiations.shift()
                this.modal = false;
                setTimeout(() => {
                    this.show_modal();
                }, 500)
            })
            this.utterance.voice = this.voic;
            this.utterance.volume = this.voice_settings.volume;
            this.utterance.pitch = this.voice_settings.pitch;
            this.utterance.rate = this.voice_settings.rate;
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
            if (!this.modal_settings) {
                this.modal_settings = true;
                return
            }
            this.modal_settings = false;
        },
        set_voic() {
            for (let i = 0; i < this.voices.length; i++) {
                if (this.voices[i].name === 'Google русский') {
                    this.voic = voices[i];
                    break;
                }
            }
        },
        suound_signal(callback) {
            const audio = new Audio(this.urls[2]);
            // Добавляем обработчик события ended
            audio.addEventListener('ended', function () {
                // Этот код будет выполнен после завершения воспроизведения аудио
                console.log('Звук закончился');
                callback();
            });
            // Воспроизводим звук
            audio.volume = this.audio_settings.volume;
            if (this.is_screen_sound){
                audio.play();
            }
            else {
                callback();
            }
        }
    }
});
app.mount('#app');