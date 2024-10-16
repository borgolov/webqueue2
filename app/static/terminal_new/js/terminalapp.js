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
            modal_text: "",
            modal: false,
        }
    },
    created() {
        this.socket = io('/queue');
        this.axios = axios

        setTimeout(this.init(), 1000)

        this.socket.on('settings', (data) => {
            this.room_id = data.room_id
        });
        this.socket.on('last_ticket', (data) => {
            this.last_ticket = data.ticket
            this.modal_text = this.last_ticket.prefix + ' ' + this.last_ticket.num
            this.show_modal()
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
        take_ticket(servicce_id) {

            if (this.checkTime(servicce_id) == false) {
                this.show_modal()
                return
            }

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
        convert_string_to_date(timeStr) {
            var [hours, minutes, seconds] = timeStr.split(':')
            var dateObj = new Date()
            dateObj.setHours(hours)
            dateObj.setMinutes(minutes)
            dateObj.setSeconds(seconds)
            return dateObj
        },
        checkTime(service_id) {
            //получение текущего дня недели
            currentDate = new Date();
            currentDayOfWeek = currentDate.toLocaleString('en-US', { weekday: 'long' })

            //получение услуги
            var_service = this.services.filter(service => service.id == service_id)[0]

            //получение offset
            currentOffset = var_service.location_offsets.find(offset => offset.day_of_week === currentDayOfWeek)

            if (currentOffset) {
                var startTime = this.convert_string_to_date(currentOffset.offset_time_down)
                var endTime = this.convert_string_to_date(currentOffset.offset_time_up)

                if (currentDate >= startTime && currentDate <= endTime) {
                    return true
                }
                else {
                    this.modal_text = "Данная услуга оказывается с " + currentOffset.offset_time_down + " - " + currentOffset.offset_time_up
                    return false
                }
            }
            else {
                this.modal_text = "Данная услуга сегодня не оказывается"
                return false
            }
        }
    }
});
app.mount('#app');