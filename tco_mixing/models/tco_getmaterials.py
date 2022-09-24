# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class tco_getmaterials(models.Model):
    _name = "tco.getmaterials"
    _description = "Get Materials"

    def _get_default_docno(self):
        return str(datetime.strftime(fields.Date.context_today, "%y%m%d"))

    name = fields.Char(string="Doc No", compute='get_name')
    x_docno = fields.Char(string="Doc No")
    docno = fields.Char(string="Doc No")

    sequence = fields.Integer(string='Sequence', default=1)
    batchno = fields.Char(string="Batch No")
    compoundno = fields.Many2one('product.product', string="Compound No")
    compoundname = fields.Char(string="Compound Name")
    mixingdate = fields.Date(string="Mixing Date", default=fields.Date.context_today)
    machineno = fields.Char(string="Machine No")
    times = fields.Float(string="Time", default=0)
    rate = fields.Float(string="Rate", default=1)
    quantity = fields.Float(string="Quanlity", default=1)
    id_tuico = fields.Integer(string="ID Tuico", required=True)
    confirmok = fields.Boolean(string="Confirm OK", default=True)
    actualweight = fields.Float(string="Actual Weight", default=0)
    outputfortest = fields.Float(string="Out Put For Test")
    issuedno = fields.Integer(string="Issue No")
    inputdetailsid = fields.Integer(string="Input Details ID")
    checkeditdata = fields.Boolean(string="Check Edit")
    weight = fields.Float(string="Weight")
    fortest = fields.Boolean(string="For Test")
    empno = fields.Char(string="Emp No")


    getmaterials_ids = fields.One2many('tco.getmaterialdetails', 'getmaterials_id', string='Mixing Details', ondelete='cascade')

    def name_get(self):
        result = []
        for res in self:
            name = res.name
            result.append((res.id, name))
        return result

    @api.depends('mixingdate')
    def get_name(self):
        for res in self:
            self.name = datetime.strftime(res.mixingdate, "%y%m%d")

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('batchno', operator, name), ('compoundno', operator, name)]
        model_ids = self._search(domain+args, limit=limit, access_rights_uid=name_get_uid)
        # return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)  # odoo 15
        return models.lazy_name_get(self.browse(model_ids).with_user(name_get_uid)) #odoo 13