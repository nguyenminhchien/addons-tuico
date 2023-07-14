# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError, RedirectWarning
import pymssql

class tco_compound_method(models.Model):
    _name = "tco.compound.method"
    _description = "Method"

    name = fields.Char('name', compute="_compute_get_name", store=True, index=True)

    method_title_id = fields.Many2one("tco.method.title", string="Group Title", store=True, required=True, copy=True)
    method_version = fields.Integer("Version", help="Curren version of method")
    method_year = fields.Integer("At Year", help="Curren Year of method")

    clm_title = fields.Char('Title', store=True, readonly=True, required=False, copy=True)

    clm_internal_code = fields.Char("Test Standard", copy=True, help="Use to get name for lines = [Test Standard][1st ASTM Code][2nd ASTM Code]")

    clm_Code = fields.Char("2nd ASTM Code",
                           help="Use to get name for lines = [Test Standard][1st ASTM Code][2nd ASTM Code]") #chuyen sang atsm_code2, sau nay xoa
    astm_code2 = fields.Char("2nd ASTM Code",
                           help="Use to get name for lines = [Test Standard][1st ASTM Code][2nd ASTM Code]")

    compound_type = fields.Selection([('AA', 'AA-NR, EPDM'),
                                      ('BA', 'BA-EPDM'),
                                      ('BC', 'BC-CR'),
                                      ('BE', 'BE-CR'),
                                      ('BF', 'BF-NBR'),
                                      ('BG', 'BG-NBR, PU'),
                                      ('BK', 'BK-NBR'),
                                      ('CA', 'CA-EPDM'),
                                      ('CH', 'CH-NBR, PU'),
                                      ('DA', 'DA-EPDM'),
                                      ('DE', 'DE-CM, CSM'),
                                      ('DF', 'DF-AEM(VA), ACM'),
                                      ('DH', 'DH-HNBR, ACM'),
                                      ('EE', 'EE-AEM(VA), ACM'),
                                      ('EH', 'EH-ACM'),
                                      ('FC', 'FC-Silicone'),
                                      ('FE', 'FE-Silicone'),
                                      ('FK', 'FK-Flosilicone'),
                                      ('GE', 'GE-Silicone'),
                                      ('HK', 'HK-FKM, AFlas'),
                                      ], string="1st ASTM Code", required=True, default="GE",
                                     help="Use to get name for lines = [Test Standard][1st ASTM Code][2nd ASTM Code]")


    method_line_ids = fields.One2many('tco.compound.method.line', 'clm_method_id', string='Method', copy=True)
    show_code = fields.Boolean("Show Code", compute="_compute_get_show_code", help="Use only check visible. if Group Title is physical will show internal_code in line")



    # _sql_constraints = [(
    #     'unique_compound_method_name',
    #     'unique (name)',
    #     'Compound Method name double key. please check!',)
    # ]

    def compute_name(self):
        # name = [clm_internal_code][compound_type]method_title_id.name
        # name = [ASTM][GE]Heat Resistance, 70 hrc at 150*C
        name = ""
        for record in self:
            if record.clm_internal_code:
                name += '[%s]' % record.clm_internal_code
            # if record.compound_type:
            #     name += '[%s]' % record.compound_type
            if record.astm_code2:
                name += '[%s]' % record.astm_code2
            if record.method_title_id:
                name += '%s' % record.method_title_id.name
            return name

    @api.depends('method_title_id', 'clm_internal_code', 'astm_code2', 'compound_type', 'method_version', 'method_year')
    def _compute_get_name(self):
        for record in self:
            record.name = record.compute_name()
            record.clm_title =record.name
            record.method_line_ids.update({'bl_change': True})

    @api.depends('method_title_id')
    def _compute_get_show_code(self):
        show_code = True
        for record in self:
            if record.method_title_id:
                if record.method_title_id.grouptitle == '0':
                    show_code = False
        record.show_code = show_code

    def name_get(self):
        result = []
        for res in self:
            result.append((res.id, res.name))
        return result

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('clm_code', operator, name)]
        model_ids = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
        # return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)  # odoo 15
        return models.lazy_name_get(self.browse(model_ids).with_user(name_get_uid)) #odoo 13

    def write(self, vals):
        self._check_doublekey(vals.get('name', self.name))
        rslt = super(tco_compound_method,self).write(vals)
        return rslt

    @api.model
    def create(self, vals):
        self._check_doublekey(vals.get('name', self.name))
        return super(tco_compound_method,self).create(vals)

    def _check_doublekey(self, keyname):
        if self.env['tco.compound.method'].search_count([('name', '=', keyname)]) > 1:
            raise UserError(_('Đã tồn tại phương thức này.'))
        return
    # -------------V15-------------------
    # @api.ondelete(at_uninstall=False)
    # def _unlink_method_line(self):
    #     if self.env['tco.specific'].search([('clm_method_line_id', 'in', self.method_line_ids.ids)], limit=1):
    #         raise UserError(_('Đã được đăng ký Project (Physical properties).'))


    def unlink(self):
        if self.env['tco.specific'].search([('clm_method_line_id', 'in', self.method_line_ids.ids)], limit=1):
            raise UserError(_('Đã được đăng ký Project (Physical properties).'))
        return super(tco_compound_method, self).unlink()

class tco_compound_method_line(models.Model):
    _name = "tco.compound.method.line"
    _description = "Method"

    name = fields.Char('Title', store=True, compute='_compute_get_name')

    # clm_Category = fields.Char("Category")
    clm_Method_Standarder = fields.Char("Method Standarder") # Duoc thay boi  method_standarder, sau nay xoa di
    method_standarder = fields.Char("Method Standarder")

    method_standarder = fields.Selection([('Hardness', 'Hardness'),
                                       ('Tensile', 'Tensile'),
                                       ('Elongation', 'Elongation'),
                                       ('Modulusat 100%', 'Modulusat 100%'),
                                       ('Specific Gravity(SG)', 'Specific Gravity(SG)'),
                                       ('Cure System', 'Cure System'),
                                       ('Volume', 'Volume'),
                                       ('Die B', 'Die B'),
                                       ('Die C', 'Die C'),
                                       ('Method B', 'Method B'),
                                       ('Nonbrittle', 'Nonbrittle'),
                                       ('Retraction', 'Retraction'),
                                       ('Method B', 'Method B'),
                                       ], string="Method Standarder", required=True, default="Hardness", store=True)

    method_line_unit = fields.Selection([
                                         ('Points', 'Points'),
                                         ('Mpa', 'Mpa'),
                                         ('%', '%'),
                                         ('kN/m', 'kN/m'),
                                         ('Type A', 'Type A'),
                                         ('Type M', 'Type M'),
                                         ('IRHD', 'IRHD'),
                                         ],
                                        string='Unit',
                                        help="Đơn vị của giá trị nhập")

    method_line_type = fields.Selection([('Shore A', 'Shore A'),
                                         ('Max', 'Max'),
                                         ('Min', 'Min')
                                         ],
                                        string='Type', store=True)

    clm_Unit = fields.Char("Unit") # Duoc thay boi  unit, sau nay xoa di
    unit = fields.Char("Unit")

    clm_internal_code = fields.Char("Test Standard", help="Use grouptitle=='physical propertirs', it in line")
    astm_code2 = fields.Char(related="clm_method_id.astm_code2", store=True,  help="Use grouptitle=='physical propertirs', it in line")

    clm_method_id = fields.Many2one("tco.compound.method", string="Method")
    sequence = fields.Integer(string='Sequence', default=1)
    method_line_ver = fields.Integer("Version")
    method_line_year = fields.Integer("At Year")

    bl_change = fields.Boolean(store=False, help="Use only check change value in tco_compound_method")
    _sql_constraints = [(
        'unique_method_name',
        'unique (name)',
        'Method name double key. please check!')
    ]

    def compute_name(self):
        # name = [Test Standard][1st ASTM Code][2nd ASTM Code]Method_Standarder
        # name = [ASTM][GE][A26]Harndness Change, max
        name = ""
        for record in self:
            if record.clm_method_id.method_title_id:
                if record.clm_method_id.method_title_id.grouptitle == '0':
                    if record.clm_internal_code:
                        name += '[%s]' % str(record.clm_internal_code or '')
                else:
                    if record.clm_method_id.clm_internal_code:
                        name += '[%s]' % str(record.clm_method_id.clm_internal_code or '')
            # if record.clm_method_id.compound_type:
            #     name = '%s[%s]' % (name, str(record.clm_method_id.compound_type or ''))
            if record.clm_method_id.astm_code2:
                name = '%s[%s]' % (name, record.clm_method_id.astm_code2)
            if record.clm_method_id.method_title_id:
                name = '%s%s' % (name, record.clm_method_id.method_title_id.name)
            if record.method_standarder:
                name = '%s, %s' % (name, record.method_standarder or '')
            if record.method_line_type:
                name = '%s, %s' % (name, record.method_line_type or '')
            if record.method_line_unit:
                name = '%s, %s' % (name, record.method_line_unit or '')
        return name

    @api.depends("method_standarder", "clm_internal_code", "method_line_type", "method_line_unit", "bl_change")
    def _compute_get_name(self):
        # Khi dung phuong thuc physical properties thi (clm_internal_code, method_line_ver, method_line_year) se duoc nhap o line
        # phuong thuc con lai thi nhap o master va update ve line de sau nay de lay dl.
        for record in self:
            record.name = record.compute_name()
            if record.clm_method_id.method_title_id:
                if record.clm_method_id.method_title_id.grouptitle != '0':
                    record.method_line_ver = record.clm_method_id.method_version
                    record.method_line_year = record.clm_method_id.method_year
                    record.clm_internal_code = record.clm_method_id.clm_internal_code


    def name_get(self):
        result = []
        for record in self:
            name = record.compute_name()
            result.append((record.id, name))
        return result

    def unlink(self):
        if self.env['tco.specific'].search([('clm_method_line_id', 'in', self.ids)], limit=1):
            raise UserError(_('Đã được đăng ký Project (Physical properties).'))
        return super(tco_compound_method_line, self).unlink()

    @api.model
    def create(self, vals):
        return super(tco_compound_method_line, self).create(vals)

    def write(self, vals):
        return super(tco_compound_method_line, self).write(vals)

