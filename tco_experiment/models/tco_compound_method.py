# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError, RedirectWarning

class tco_compound_method(models.Model):
    _name = "tco.compound.method"
    _description = "Method"

    name = fields.Char('name', related='clm_title', store=True)
    clm_title = fields.Char('Title', store=True, required=True, copy=True)
    clm_Code = fields.Char("Code", required=True)
    clm_internal_code = fields.Char("Internal Code", copy=True)
    method_line_ids = fields.One2many('tco.compound.method.line', 'clm_method_id', string='Method', copy=True)

    def name_get(self):
        result = []
        strintercode1 = ""
        strintercode2 = ""
        strcode1 = ""
        strcode2 = ""
        for res in self:
            if res.clm_internal_code:
                strintercode1 = "["
                strintercode2 = "]"
            if res.clm_Code:
                strcode1 = "["
                strcode2 = "]"
            name = strintercode1 + (res.clm_internal_code or '') + strintercode2 + strcode1 + (res.clm_Code or '') + strcode2 + (res.clm_title or '')
            result.append((res.id, name))
        return result

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('clm_title', operator, name), ('clm_Code', operator, name)]
        model_ids = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
        # return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)  # odoo 15
        return models.lazy_name_get(self.browse(model_ids).with_user(name_get_uid)) #odoo 13

    # -------------V15-------------------
    # @api.ondelete(at_uninstall=False)
    # def _unlink_method_line(self):
    #     if self.env['tco.specific'].search([('clm_method_line_id', 'in', self.method_line_ids.ids)], limit=1):
    #         raise UserError(_('Used by Project (Physical properties).'))


    def unlink(self):
        if self.env['tco.specific'].search([('clm_method_line_id', 'in', self.method_line_ids.ids)], limit=1):
            raise UserError(_('Used by Project (Physical properties).'))
        return super(tco_compound_method, self).unlink()

class tco_compound_method_line(models.Model):
    _name = "tco.compound.method.line"
    _description = "Method"

    name = fields.Char('Title', store=True, compute='_compute_get_name')

    clm_Category = fields.Char("Category")
    clm_Method_Standarder = fields.Char("Method Standarder")
    clm_Comparison = fields.Char("Comparison")
    clm_Unit = fields.Char("Unit")
    clm_internal_code = fields.Char("Internal Code")
    clm_method_id = fields.Many2one("tco.compound.method", string="Method")
    sequence = fields.Integer(string='Sequence', default=1)

    @api.depends("clm_Category", "clm_Method_Standarder", "clm_Unit", "clm_method_id.clm_Code")
    def _compute_get_name(self):
        strintercode1 = ""
        strintercode2 = ""
        strcode1 = ""
        strcode2 = ""
        for record in self:
            if record.clm_internal_code:
                strintercode1 = "["
                strintercode2 = "]"
            if record.clm_method_id.clm_Code:
                strcode1 = "["
                strcode2 = "]"
            record.name = strintercode1 + (record.clm_internal_code or '') + strintercode2 + strcode1 + (record.clm_method_id.clm_Code or '') + strcode2 + (record.clm_Method_Standarder or '')

    def name_get(self):
        result = []
        strintercode1 = ""
        strintercode2 = ""
        strcode1 = ""
        strcode2 = ""
        strunit1 = ""
        strunit2 = ""
        for record in self:
            if record.clm_internal_code:
                strintercode1 = "["
                strintercode2 = "]"
            if record.clm_method_id.clm_Code:
                strcode1 = "["
                strcode2 = "]"
            if record.clm_Unit:
                strunit1 = "("
                strunit2 = ")"
            name = strintercode1 + (record.clm_internal_code or '') + strintercode2 \
                   + strcode1 + (record.clm_method_id.clm_Code or '') + strcode2 \
                   + (record.clm_Method_Standarder or '') \
                   + strunit1 + (record.clm_Unit or '') + strunit2
            result.append((record.id, name))
        return result

    # -------------V15-------------------
    # @api.ondelete(at_uninstall=False)
    # def _unlink_method_line(self):
    #     if self.env['tco.specific'].search([('clm_method_line_id', 'in', self.ids)], limit=1):
    #         raise UserError(_('Used by Project (Physical properties).'))


    def unlink(self):
        if self.env['tco.specific'].search([('clm_method_line_id', 'in', self.ids)], limit=1):
            raise UserError(_('Used by Project (Physical properties).'))
        return super(tco_compound_method_line, self).unlink()



