# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta
import datetime


class Kursus(models.Model):
    _name = 'training.kursus'
    _inherit = 'mail.thread'
    _description = "Kursus untuk odoo"
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('done', 'Done'),
        ], string='Status', readonly=True, copy=False, default='draft')
    
    name = fields.Char(string="Judul", required=True,  track_visibility='onchange')
    description = fields.Text(readonly=True, track_visibility='onchange')
    session_ids = fields.One2many('training.sesi', 'course_id', string="Sesi",  track_visibility='onchange')
    responsible_id = fields.Many2one('res.users', ondelete='set null', string="Penanggung Jawab", index=True,  track_visibility='onchange')
    
    on_weekend = fields.Boolean('Kursus Buka Saat Weekend', default=False, help="Klik Centang apabila Kursus ini tersedia pada saat weekend")
    date_start = fields.Date(string="Kursus dimulai")
    date_done = fields.Date(string="Kursus berakhir")
    result_weekend = fields.Char(string='result')
    
    @api.onchange('on_weekend','result_weekend')
    def _verify_on_weekend(self):
        if self.on_weekend == True:
            return{
                'value' : {
                    'result_weekend': 'Buka Saat Weekend'
                },
                'warning' : {
                    'message' : 'Buka Saat Weekend'
                }
            }
        else:
            return{
                'value' : {
                    'result_weekend': 'Tidak Buka Saat Weekend'
                }
            }
    _sql_constraints = [
                    ('name_description_cek', 'CHECK(name != description)', 'Judul kursus dan keterangan tidak boleh sama '),
                    ('name_unik', 'UNIQUE(name)', 'Judul kursus harus unik')
    ]
    
    @api.multi
    def copy(self, default=None):
        default = dict(default or {})
        copied_count = self.search_count([('name', '=like', "Copy of {}%".format(self.name))]) # Searching judul kursus yang sama dan menyimpannya pada variable copied_count 

        if not copied_count: # Cek isi variable copied_count (hasil searching) 
            new_name = "Copy of {}".format(self.name) # Jika proses searching judul yang sama tidak ditemukan, maka judul baru akan dikasih imbuhan 'Copy of'
        else:
            new_name = "Copy of {} ({})".format(self.name, copied_count) # Jika proses searching judul yang sama ditemukan, maka judul baru akan dikasih imbuhan 'Copy of' dan angka terakhir duplicate
        
        default['name'] = new_name # Mereplace value field name dengan yang sudah di sesuaikan
        return super(Kursus, self).copy(default)
    
    
    
    @api.multi
    def action_confirm(self):
        self.write({'state': 'open'})
 
    @api.multi
    def action_cancel(self):
        self.write({'state': 'draft'})
 
    @api.multi
    def action_close(self):
        self.write({'state': 'done'})



class Sesi(models.Model):
    _name = 'training.sesi'
    _description = 'Ini merupakan class untuk sesi'
    
    name = fields.Char(required=True)
    # case study : 1, bagaimana caranya supaya tgl saat dimulai sesi tidak lebih kecil dari saat mulai Kursus
    start_date = fields.Date(string="Sesi dimulai", required=True)
    # end of case study : 1
    duration = fields.Float(string='', digits=(6,2), help="Durasi Hari", required=True)
    seats = fields.Integer(string='Jumlah Kursi')
    instructor_id = fields.Many2one('res.partner', string='Instructor', domain=["|",('instructor','=',True),("category_id.name","ilike","Pengajar")]) 
    course_id = fields.Many2one('training.kursus', string='Kursus', required=True, ondelete='cascade')
    attendee_ids = fields.Many2many('res.partner', string='Peserta', domain=[('instructor','=',False)])
    taken_seats = fields.Float(compute='_taken_seats', string='Kursi Terisi')
    attendees_count = fields.Integer(string="Jumlah Peserta", compute='_get_attendees_count', store=True)
    color = fields.Integer('Warna')
    
    # solusi untuk case study : 1
    global_start_date = fields.Date(string='Start Date Kursus Utama', related="course_id.date_start")
    # end of case study : 1
    
    #case study : 2, bagaimana supaya tanggal di sesi tidak melebihi tanggal end_date di kursus
    
    # solusi untuk case study : 2
    global_end_date = fields.Date(string='End Date Kursus Utama', related="course_id.date_done")
    # end of case study : 2
    
    end_date = fields.Date(string="Tanggal Selesai", store=True, compute='_get_end_date', inverse='_set_end_date')
    
    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for r in self:
            # Pengecekan jika field duration & start_date tidak diisi, maka field end_date akan di update sama seperti field start_date
            if not (r.start_date and r.duration): 
                r.end_date = r.start_date
                continue
    
            # Membuat variable start yang isinya tanggal dari field start_date 
            start = fields.Date.from_string(r.start_date)
            
            # Membuat variable duration yang isinya durasi hari dari field duration
            # Durasi hari dikurangi 1 detik agar start_date masuk kedalam durasi hari
            duration = timedelta(days=r.duration, seconds=-1)
            
            # Mengupdate field end_date dari perhitungan variabel start ditambah variabel duration 
            r.end_date = start + duration
    
    def _set_end_date(self):
        for r in self:
            if not (r.start_date and r.end_date):
                continue
        
            # Membuat variable start_date yang isinya tanggal dari field start_date
            start_date = fields.Date.from_string(r.start_date)
            
            # Membuat variable end_date yang isinya tanggal dari field end_date
            end_date = fields.Date.from_string(r.end_date)
            
            # Mengupdate field duration (jika ada perubahan dari field end_date) dari perhitungan variabel end_date dikurangi variabel start_date (ditambah 1 hari agar end_date termasuk durasi hari) 
            r.duration = (end_date - start_date).days + 1
    
    @api.depends('seats','attendee_ids')
    def _taken_seats(self):
        for r in self :
            if not r.seats:
                r.taken_seats = 0.0
            else:
                r.taken_seats = 100.0 * len(r.attendee_ids) / r.seats

    # solusi untuk case study : 1
    @api.onchange('start_date','global_start_date')
    def _verify_date(self):
        if self.start_date:
            if self.start_date < self.global_start_date:
                return{
                    'warning' : {
                        'title' : 'Date Validator',
                        'message' : 'Tanggal Invalid, tanggal Harus Lebih besar dari {} '.format(self.global_start_date),
                    },
                    'value' : {
                        'start_date' : ''
                    }
                }
    # end of case study : 1
    
    # solusi untuk case study : 2
    @api.onchange('start_date','global_end_date','duration')
    def _verify_end_date(self):
        if self.start_date:
            end_date_by_duration = self.start_date + datetime.timedelta(days=self.duration)
            print("wkwkkwkwkwkkwkwkkwkwkkwkw")
            print(self.duration)
            if end_date_by_duration > self.global_end_date:
                return{
                    'warning' : {
                        'title' : 'Date Validator',
                        'message' : 'Tanggal Invalid, tanggal tidak boleh melebihi {} '.format(self.global_end_date),
                    },
                    'value' : {
                        'duration' : '1'
                    }
                }
            elif self.duration < 1:
                return{
                    'warning' : {
                        'title' : 'Duration Validator',
                        'message' : 'Duration Invalid, tidak boleh kurang dari 1',
                    },
                    'value' : {
                        'duration' : '1'
                    }
                }
            
    # end of case study : 2
    
    @api.onchange('seats','attendee_ids')
    def _verify_valid_seats(self):
        if self.seats < 0: # cek nilai field seats, jika dibawah 0 (negatif), maka masuk kondisi if
            return {
                    'value': {
                                'seats': len(self.attendee_ids) or 1 # mengisi field seats dengan nilai jumlah peserta atau 1
                            },
                    'warning': {
                                'title': "Nilai Jumlah Kursi Salah", # judul pop up
                                'message': "Jumlah Kursi Tidak Boleh Negatif" # pesan pop up
                                }
                    }

        if self.seats < len(self.attendee_ids): # cek nilai field seats (jumlah kursi) apakah lebih kecil dari field attendee_ids (jumlah peserta), jika iya maka masuk kondisi if
            return {
                    'value': {
                                'seats': len(self.attendee_ids) # mengisi field seats dengan nilai jumlah peserta
                            },
                    'warning': {
                                'title': "Peserta Terlalu Banyak", # judul pop up
                                'message': "Tambahkan Kursi atau Kurangi Peserta" # pesan pop up
                                }
                    }
    
    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendees(self):
        for r in self:
            if r.instructor_id and r.instructor_id in r.attendee_ids: # Jika field instructor_id (Instruktur) diisi DAN instructor_id ada di tabel attendee_ids (Peserta), maka munculkan pesan error 
                return {
                        'warning': {
                                    'title': "invalid input", # judul pop up
                                    'message': "Seorang instruktur tidak boleh menjadi peserta" # pesan pop up
                                    }
                    }
    
    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for r in self:
            # Mengupdate field attendees_count berdasarkan jumlah record di tabel peserta 
            r.attendees_count = len(r.attendee_ids)
            
    @api.multi 
    def print_sesi(self):
        return self.env.ref("training_odoo.action_print_sesi").report_action(self)

class Bahan(models.Model):
    _name = 'training.bahan'
    _description = 'Bahan bahan'
    
    name = fields.Char(string='Materi')
    course_id = fields.Many2one('training.kursus', string='Kursus',required=True, ondelete='cascade')
    bahan = fields.Selection([('ppt', 'PPT'),('buku','Buku')], string='Bahan')
    