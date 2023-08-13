const app = Vue.createApp({
    data() {
        return {
            socket: null,
            axios: null,

            message: 'Yo hello wsup',
            room_id: null,
            location: "location",
            organization: "organiztion",
            urls: ["/api/v1/operator_settings", "/static/worker_new/image/push.png"],
            operator: {},
            last_ticket: {
                num: 0,
                prefix: "prefix",
                time: "",
                service: {
                    id: 0,
                    name: "service"
                }
            },
            current_ticket: {
                num: 0,
                prefix: "prefix",
                time: "",
                service: {
                    id: 0,
                    name: "service"
                }
            },
            stat: {},
            services: [],
            changed_service_id: 0,
            is_call_client: true,
        }
    },
    created() {
        this.socket = io('/queue');
        this.axios = axios

        setTimeout(this.init(), 1000)
        
        this.socket.on('settings', (data) => {
            this.room_id = data.room_id
        });
        this.socket.on('state', (data) => {
            this.stat = data
        });
        this.socket.on('ticket', (data) => {
            this.current_ticket = null === data || void 0 === data ? void 0 : data.ticket
        });
        this.socket.on('newticket', (data) => {
            this.push(data?.ticket?.service?.name)
        });
    },
    methods: {

        init() {
            this.axios.get(this.urls[0]).then(resp => {
                this.location = resp.data.location
                this.organization = resp.data.organization
                this.operator = resp.data.operator
                this.services = resp.data.services
                console.log(this.organization)
            }).catch(error => {
                console.error(error);
            });
        },
        call_client() {
            if (this.is_call_client){
                this.is_call_client = false
                this.socket.emit('call_client', {
                    room: this.room_id
                })
                setTimeout(() => {
                    this.is_call_client = true
                }, 3000)
            }
        },
        confirm_client() {
            if (confirm("выполнить?")) {
                this.socket.emit('confirm_client', {
                    room: this.room_id
                })
            } 
        },
        delay_client() {
            if (confirm("выполнить?")) {
                this.socket.emit('delay_client', {
                    room: this.room_id
                })
            }
        },
        call_delay_client() {
            if (confirm("выполнить?")) {
                this.socket.emit('call_delay_client', {
                    room: this.room_id
                })
            }
        },
        change_service_client(service_id) {
            if (service_id == 0) return;
            if (confirm("выполнить?")) {
                this.socket.emit('change_service_client', {
                    room: this.room_id,
                    service_id: service_id
                })
            }
        },
        push(service) {
            if ('Notification' in window) {
                // Проверяем, разрешено ли показывать уведомления
                if (Notification.permission === 'granted') {
                    // Создаем новое уведомление
                    const notification = new Notification('Заголовок уведомления', {
                        body: 'Новый талон с услугой: '+service,
                        icon: this.urls[1], // путь к изображению для иконки уведомления (опционально)
                    });
                    // Обработчик клика на уведомлении
                    notification.onclick = function () {
                        console.log('Уведомление было кликнуто');
                    };
                } 
                else if (Notification.permission !== 'denied') {
                    // Если разрешение не получено, запрашиваем его у пользователя
                    Notification.requestPermission().then(function (permission) {
                        if (permission === 'granted') {
                            // Повторно создаем уведомление после получения разрешения
                            // ...
                        }
                    });
                }
            }
        }
    }
});
app.mount('#app');