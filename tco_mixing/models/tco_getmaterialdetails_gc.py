# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class tco_getmaterialdetails_GC(models.Model):
    _name = "tco.getmaterialdetails_gc"
    _description = "Get Materials Details GC"

    name = fields.Char(related='materialno.default_code')
    sequence = fields.Integer(string='Sequence', default=1)

    weight = fields.Float('Weight')
    id_tuico = fields.Integer('ID Tuico')
    mid_tuico = fields.Integer('Master ID')
    ref = fields.Char('Ref')
    confirmok = fields.Boolean('Comfirm OK')
    note = fields.Char('Note')
    weightactual = fields.Float('Weight Actual')
    batchnostock = fields.Char('Batch No Stock')

    materialno = fields.Many2one('product.product', string="Material No", required=True)
    getmaterials_id = fields.Many2one('tco.getmaterials_gc', string='Mixing Details', ondelete='cascade')

    docno = fields.Char(related='getmaterials_id.name')
    mixingdate = fields.Date(related='getmaterials_id.mixingdate')
    quantity = fields.Float(related='getmaterials_id.quantity')

    def name_get(self):
        result = []
        for res in self:
            name = res.name
            result.append((res.id, name))
        return result
