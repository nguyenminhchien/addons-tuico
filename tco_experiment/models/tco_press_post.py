# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class tco_press_post(models.Model):
    _name = "tco.press.post"
    _description = "Press Post Cure"

    @api.depends("clm_testobject", "clm_molding_temp", "clm_molding_time", "clm_postcure_temp", "clm_postcure_time")
    def _compute_get_name(self):
        for res in self:
            res.name = "[%s]-Molding(Temp*Time)(%s*%s)-Post Cure(Temp*Time)(%s*%s)" \
                       % (res.clm_testobject or '', res.clm_molding_temp or '', res.clm_molding_time or '', res.clm_postcure_temp, res.clm_postcure_time)

    name = fields.Char(string="name", compute=_compute_get_name, store=True, copy=True)
    sequence = fields.Integer(string='Sequence', default=1)

    clm_testobject = fields.Selection([('slab', 'SLAB'),
                                       ('buttonsmall', 'Button small 6.0x13(mm)'),
                                       ('buttonbig', 'Button big 12.5x29(mm)')], string="Item", requests=True, copy=True)
    clm_molding_temp = fields.Char(string='Molding Temp', copy=True)
    clm_molding_time = fields.Char(string='Molding Time(s)', copy=True)
    clm_postcure_temp = fields.Char(string='Post Cure Temp', copy=True)
    clm_postcure_time = fields.Char(string='Post Cure Time(h)', copy=True)
    clm_result = fields.Selection([('ok', 'OK'), ('ng', 'NG')], string='Result', copy=True)
    clm_description = fields.Char(string='Notes')
    task_id = fields.Many2one('tco.task', string='Task ID', copy=True)

    def name_get(self):
        result = []
        for res in self:
            name = res.name
            result.append((res.id, name))
        return result

    def copy_record(self, default=None):
        if default is None:
            default = {}
        # if 'name' not in default:
            # default['name'] = _("(copy of) %s", self.name)
        return super(tco_press_post, self).copy(default)


    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('clm_testobject', operator, name)]
        # return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid) # odoo V15
        model_ids = self._search(domain + args, limit=limit, access_rights_uid=name_get_uid) # odoo V13
        return models.lazy_name_get(self.browse(model_ids).with_user(name_get_uid))  # odoo V13

