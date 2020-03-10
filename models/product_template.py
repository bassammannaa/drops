# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    name_ar = fields.Char(string="Arabic Name", required=False, )
    old_id = fields.Integer(string="Old ID", required=False,)


class ProductProduct(models.Model):
    _inherit = "product.product"

    old_id = fields.Integer(string="Old ID", required=False,)