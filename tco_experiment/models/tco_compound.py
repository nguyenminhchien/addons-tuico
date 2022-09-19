# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError

class tco_compound(models.Model):
    _name = "tco.compound"
    _description = "compound model"

    name = fields.Char(string='Compound', required=True, readonly=False, store=True)

    clm_compound_ids = fields.One2many('tco.project', 'clm_compound_id', 'Project List')

    # ---------odoo V13----------------------
    def unlink(self):
        if self.env['tco.project'].search([('clm_compound_id', 'in', self.ids)], limit=1):
            raise UserError(_('Used by Project.'))
        return super(tco_compound, self).unlink()
