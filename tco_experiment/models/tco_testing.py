# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class tco_testing(models.Model):
    _name = "tco.testing"
    _description = "Testing"

    @api.depends("clm_testobject", "clm_molding_temp", "clm_molding_time", "clm_postcure_temp", "clm_postcure_time")
    def _compute_get_name(self):
        for res in self:
            res.name = "[%s]-Molding(Temp*Time)(%s*%s)-Post Cure(Temp*Time)(%s*%s)" \
                       % (res.clm_testobject or '', res.clm_molding_temp or '', res.clm_molding_time or '', res.clm_postcure_temp, res.clm_postcure_time)

    name = fields.Char(string="name", compute=_compute_get_name, store=True)
    sequence = fields.Integer(string='Sequence', default=1)

    clm_testobject = fields.Char(string='Item', copy=False)
    method_line_id = fields.Many2one('tco.method.title', string='Group Name')

    # Ngoai Quan
    clm_flash = fields.Char(string='Flash(bazo)(max:0.10mm')
    clm_appearance = fields.Char(string='Appearance(Ngoại quan)')
    clm_molddirty = fields.Char(string='Mold dirty(khuôn dơ/5mold)')
    clm_sticky = fields.Char(string='Sticky to mold(dính khuôn/5mold)')
    clm_flow = fields.Char(string='Material flow(độ tan của liệu)')
    clm_release = fields.Char(string='Release agent(dùng nước tách khuôn)')
    clm_loose = fields.Char(string='Loose flash(bazo dính)')
    # ==============
    # Test Sample
    clm_molding_temp = fields.Char(string='Molding Temp')
    clm_molding_time = fields.Char(string='Molding Time')
    clm_postcure_temp = fields.Char(string='Post Cure Temp')
    clm_postcure_time = fields.Char(string='Post Cure Time')

    task_id_name = fields.Char(string='Task Name', related="task_id.name", store=True)
    task_id_compound = fields.Char(string='Task Name', related="task_id.clm_compound_id", store=True)

    method_id = fields.Selection([('typem', 'Type M'), ('typea', 'Type A'), ('irhd', 'IRHD')], string='Method ID')

    clm_request_value = fields.Char('Request Value')

    # , compute = "_compute_value_before"

    clm_result_before = fields.Char('Before')
    clm_result_min_before = fields.Float('Before Min')
    clm_result_max_before = fields.Float('Before Max')

    # , compute = "_compute_value_result"
    clm_result_value = fields.Char('After')
    clm_result_min_value = fields.Float('After Min')
    clm_result_max_value = fields.Float('After Max')
    clm_result = fields.Selection([('ok', 'OK'), ('ng', 'NG')], string='Result')
    clm_description = fields.Char(string='Notes')

    task_id = fields.Many2one('tco.task', string='Task ID')
    project_id = fields.Integer(related="task_id.project_id.id")

    def name_get(self):
        result = []
        for res in self:
            name = res.name
            result.append((res.id, name))
        return result

    def copy_record(self, default=None):
        if default is None:
            default = {}
        return super(tco_testing, self).copy(default)

    @api.model
    def default_get(self, fields):
        res = super(tco_testing, self).default_get(fields)
        if 'task_id' in fields:
            res['task_id'] = self._context.get('active_id', False)
        return res

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('clm_testobject', operator, name)]
        # return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid) # odoo V15
        model_ids = self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)  # odoo V13
        return models.lazy_name_get(self.browse(model_ids).with_user(name_get_uid))  # odoo V13

    @api.depends('clm_result_min_value', 'clm_result_max_value')
    def _compute_value_result(self):
        name = None
        for record in self:
            if record.clm_result_min_value and record.clm_result_min_value > 0:
                name = '%s' % record.clm_result_min_value or ''
            if record.clm_result_max_value and record.clm_result_max_value > 0:
                name += '~%s' % record.clm_result_max_value or ''
        record.clm_result_value = name

    @api.depends('clm_result_min_before', 'clm_result_max_before')
    def _compute_value_before(self):
        name = None
        for record in self:
            if record.clm_result_min_before and record.clm_result_min_before > 0:
                name = '%s' % record.clm_result_min_before or ''
            if record.clm_result_max_before and record.clm_result_max_before > 0:
                name += '~%s' % record.clm_result_max_before or ''
        # record.clm_result_before = name or ''

    # @api.onchange('clm_result_value')
    # def _onchange_result_value(self):
    #     fl_min = 0.0
    #     fl_max = 0.0
    #     if self.clm_result_value:
    #         strcap = self.clm_result_value
    #         arrstrcap = strcap.split('~')
    #         for i in range(len(arrstrcap)):
    #             if i == 0:
    #                 fl_min = fl_max = float(arrstrcap[i])
    #             if i == 1:
    #                 if float(arrstrcap[i]) > 0:
    #                     fl_max = float(arrstrcap[i])
    #         self.clm_result_min_value = fl_min
    #         self.clm_result_max_value = fl_max

    def action_view_appearance(self):
        self.ensure_one()
        return {
            'name': self.display_name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'tco.testing',
            'res_id': self.id,
        }

    def action_view_form_task(self):
        self.ensure_one()
        return {
            'name': self.task_id_name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'tco.task',
            'res_id': self.task_id.id,
        }
