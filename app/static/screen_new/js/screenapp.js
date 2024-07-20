const app = Vue.createApp({
    data() {
        return {
            socket: null,
            axios: null,
            room_id: "",
            location: "location",
            organization: "organization",
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
            notifications: [],
            stat: {},
            modal: false,
            settings: false,
            voices: [],
            voic: null,
            utterance: null,
            is_screen_sound: true,
            modal_settings: false,
            voice_settings: {
                volume: 1,
                rate: 1,
                pitch: 1
            },
            audio_settings: {
                volume: 1
            }
        }
    },
    created() {
        this.socket = io('/queue');
        this.axios = axios;
        this.get_voices();

        this.$nextTick(() => {
            this.init();
            this.set_voic();
        });

        this.socket.on('call_client', (data) => {
            this.notifications.push(data);
            this.show_modal();
        });
        this.socket.on('state', (data) => {
            this.stat = data;
        });
    },
    methods: {
        init() {
            this.axios.get(this.urls[0]).then(resp => {
                this.location = resp.data.location;
                this.organization = resp.data.organization;
                this.device = resp.data.device;
            }).catch(error => {
                console.error('Error fetching device settings:', error);
            });
        },
        show_modal() {
            if (this.notifications.length === 0) return;

            const notific = this.notifications[0];
            this.last_notific.operator = notific?.operator?.name;
            this.last_notific.ticket = notific?.ticket.prefix + notific?.ticket.num;

            if (!this.modal) {
                this.modal = true;
                this.suound_signal(() => {
                    if (this.voic !== null) {
                        this.voice(notific, this.last_notific.ticket);
                    } else {
                        setTimeout(() => {
                            this.modal = false;
                            this.notifications.shift();
                            setTimeout(() => {
                                this.show_modal();
                            }, 500);
                        }, 3000);
                    }
                });
            }
        },
        voice(notific, string) {
            this.utterance = new SpeechSynthesisUtterance(notific?.operator?.duber.replace('@', string));
            this.utterance.addEventListener('end', () => {
                this.notifications.shift();
                this.modal = false;
                setTimeout(() => {
                    this.show_modal();
                }, 500);
            });
            this.utterance.voice = this.voic;
            this.utterance.volume = this.voice_settings.volume;
            this.utterance.pitch = this.voice_settings.pitch;
            this.utterance.rate = this.voice_settings.rate;
            speechSynthesis.speak(this.utterance);
        },
        cli() {
            console.log("click");
        },
        get_voices() {
            this.voices = window.speechSynthesis.getVoices();
            window.speechSynthesis.onvoiceschanged = () => {
                this.voices = window.speechSynthesis.getVoices();
            };
        },
        show_voices_select() {
            this.get_voices();
            this.modal_settings = !this.modal_settings;
        },
        set_voic() {
            for (let i = 0; i < this.voices.length; i++) {
                if (this.voices[i].name === 'Google русский') {
                    this.voic = this.voices[i];
                    break;
                }
            }
        },
        suound_signal(callback) {
            const audio = new Audio(this.urls[2]);
            audio.addEventListener('ended', () => {
                console.log('Звук закончился');
                callback();
            });
            audio.volume = this.audio_settings.volume;
            if (this.is_screen_sound) {
                audio.play();
            } else {
                callback();
            }
        }
    }
});
app.mount('#app');