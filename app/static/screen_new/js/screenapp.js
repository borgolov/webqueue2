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
                "/static/screen_new/sound/screen.mp3",
                "/static/sounds/"
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
            is_screen_sound: false,
            is_static_voice: false,
            modal_settings: false,
            voice_settings: {
                volume: 1,
                rate: 1,
                pitch: 1
            },
            audio_settings: {
                volume: 1
            },
            staic_voice_settings: {
                is_window: false,
                voice_volume: 1
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

            
            if (this.is_static_voice) {
                if (!this.modal) {
                    this.modal = true;
                    this.suound_signal(() => {
                        // Используем записанные звуки

                        // === Извлекаем номер окна из строки вида "Окно 1" ===
                        const windowMatch = notific?.operator?.name.match(/\d+/);
                        const windowNumStr = windowMatch ? windowMatch[0] : '1';
                        console.log(windowNumStr)
                        console.log(notific.ticket.prefix)
                        console.log(notific.ticket.num)

                        this.static_voice(
                            this.cleanPrefix(notific.ticket.prefix),
                            notific.ticket.num,
                            windowNumStr
                        );
                    });
                }
            }
            else {
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
        },
        cleanPrefix(prefix) {
            if (!prefix) return '';
            return prefix.charAt(0).toLowerCase();
        },
        static_voice(prefix, ticket, window) {
            // --- Обработка номера талона ---
            const numTicket = parseInt(ticket, 10);
            if (isNaN(numTicket) || numTicket < 1 || numTicket > 2000) {
                console.warn("Некорректный номер талона:", ticket);
                return;
            }

            const ticketParts = [];
            let rem = numTicket;

            if (numTicket <= 19) {
                ticketParts.push(numTicket);
            } else {
                const th = Math.floor(rem / 1000);
                if (th) { ticketParts.push(th * 1000); rem %= 1000; }

                const h = Math.floor(rem / 100);
                if (h) { ticketParts.push(h * 100); rem %= 100; }

                if (rem >= 11 && rem <= 19) {
                    ticketParts.push(rem);
                } else {
                    const t = Math.floor(rem / 10);
                    const u = rem % 10;
                    if (t > 0) ticketParts.push(t * 10);
                    if (u > 0) ticketParts.push(u);
                }
            }

            // --- Обработка номера окна ---
            const numWindow = parseInt(window, 10);
            if (isNaN(numWindow) || numWindow < 1 || numWindow > 2000) {
                console.warn("Некорректный номер окна:", window);
                return;
            }

            const windowParts = [];
            rem = numWindow;

            if (numWindow <= 19) {
                windowParts.push(numWindow);
            } else {
                const th = Math.floor(rem / 1000);
                if (th) { windowParts.push(th * 1000); rem %= 1000; }

                const h = Math.floor(rem / 100);
                if (h) { windowParts.push(h * 100); rem %= 100; }

                if (rem >= 11 && rem <= 19) {
                    windowParts.push(rem);
                } else {
                    const t = Math.floor(rem / 10);
                    const u = rem % 10;
                    if (t > 0) windowParts.push(t * 10);
                    if (u > 0) windowParts.push(u);
                }
            }

            // --- Формируем последовательность звуков ---
            const base = this.urls[3]; // "/static/sounds/"
            const sequence = [
                base + "client.wav",
                base + prefix.toLowerCase() + ".wav",
                ...ticketParts.map(n => base + n + ".wav")
            ];

            // Добавляем "окно N" только если включено в настройках
            if (this.staic_voice_settings.is_window) {
                sequence.push(base + "window.wav");
                sequence.push(...windowParts.map(n => base + n + ".wav"));
            }

            // --- Воспроизводим по очереди ---
            let index = 0;
            const playNext = () => {
                if (index >= sequence.length) {
                    // Завершено — закрываем модалку и переходим к следующему
                    this.modal = false;
                    this.notifications.shift();
                    setTimeout(() => {
                        this.show_modal();
                    }, 500);
                    return;
                }

                const audio = new Audio(sequence[index]);
                audio.volume = this.staic_voice_settings.voice_volume;

                audio.onended = () => {
                    index++;
                    playNext();
                };

                audio.onerror = (err) => {
                    console.error("Ошибка загрузки звука:", sequence[index], err);
                    index++;
                    playNext(); // пропускаем проблемный файл
                };

                audio.play().catch(err => {
                    console.warn("Не удалось воспроизвести звук:", err);
                    index++;
                    playNext();
                });
            };

            playNext();
        }
    }
});
app.mount('#app');