# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class tco_specific(models.Model):
    _name = "tco.specific"

    _description = "Specific"

    name = fields.Char(string="Method Name", store=True)
    sequence = fields.Integer(string='Sequence', default=1)
    project_id = fields.Many2one('tco.project', string='project ID', readonly=True, copy=True, tracking=True)
    clm_method_line_id = fields.Many2one('tco.compound.method.line', string='Method Request', store=True, tracking=True)
    clm_request_value = fields.Char('Request Value', tracking=True)
    specific_version = fields.Integer("Version", store=True)
    specific_year = fields.Integer("At Year", store=True)
    specific_unit = fields.Char("Unit", store=True)

    @api.onchange('clm_method_line_id')
    def _compute_year_ver_unit(self):
        for record in self:
            if record.clm_method_line_id:
                record['name'] = self.clm_method_line_id.name
                if record.clm_method_line_id.method_line_ver:
                    record['specific_version'] = record.clm_method_line_id.method_line_ver
                if record.clm_method_line_id.method_line_year:
                    record['specific_year'] = record.clm_method_line_id.method_line_year
                if record.clm_method_line_id.method_line_unit:
                    record['specific_unit'] = record.clm_method_line_id.method_line_unit

    def name_get(self):
        result = []
        for record in self:
            name = record.name or ''
            result.append((record.id, name))
        return result


    # ---------odoo V13----------------------
    def unlink(self):
        if self.env['tco.result'].search([('clm_method_line_id', 'in', self.ids)], limit=1):
            raise UserError(_('Used by Task (Physical properties result).'))
        return super(tco_specific, self).unlink()

    def _update_line(self, values):
        Mappeds = self.mapped('project_id')
        for Mapped in Mappeds:
            update_lines = self.filtered(lambda x: x.project_id == Mapped)
            msg = "<b>" + _("The method specific has been updated.") + "</b><ul>"
            for line in update_lines:
                msg += "<li> %s: " % line.clm_method_line_id.name
                msg += _("Method specific: %s -> %s " % (line.clm_request_value, values["clm_request_value"])) #odoo V13
            msg += "</ul>"
            Mapped.message_post(body=msg)

    @api.model
    def create(self, values):

        return super(tco_specific, self).create(values)

    def write(self, values):

        result = super(tco_specific, self).write(values)
        if 'clm_request_value' in values:
            self._update_line(values)
        return result


