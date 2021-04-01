from odoo import api, fields, models

class Partner(models.Model):
    _inherit = 'res.partner'
    
    instructor = fields.Boolean(string='Instructor')
    session_ids = fields.Many2many('training.sesi', string='Menghadiri Session', readonly=True)
    
    statused = fields.Char(string='Statused')
    is_graduated = fields.Boolean(string='Graduated', default=True)
    ktp = fields.Char(string='KTP')