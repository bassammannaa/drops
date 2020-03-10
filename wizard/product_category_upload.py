# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
import xlrd
import tempfile
import base64

logger = logging.getLogger(__name__)


class ProductCategoryUpload(models.TransientModel):
    _name = "drops.product.category.upload"
    _description = "Product Category Upload"

    data = fields.Binary('File', required=True, attachment=False)
    filename = fields.Char('File Name', required=True)
    overwrite = fields.Boolean('Overwrite Existing Date',
                               default=True,)

    def import_data(self):
        try:
            # Open File for read
            #=====================
            file_path = tempfile.gettempdir() + '/file.xls'
            f = open(file_path, 'wb')
            f.write(base64.decodebytes(self.data))
            f.close()
            book = xlrd.open_workbook(file_path)

            # Validations
            #=============
            if book.nsheets != 1:
                raise ValidationError("Number of Excel book is less or more than one book.")

            sheet = book.sheet_by_index(0)
            if sheet.ncols != 4:
                raise ValidationError("Number of book Columns are less or more than 4 columns.")
            if sheet.nrows < 2:
                raise ValidationError("Number of book records are less or more than 1 row.")

            product_cat_saleable = self.env['product.category'].search([('name', '=', 'Saleable')], limit=1)
            if not product_cat_saleable:
                raise ValidationError("Parent Category Saleable is not found.")
            else:
                product_cat_saleable_id = product_cat_saleable.id

            # Clear data
            # =============
            product_cat_obj = self.env['product.category'].search([('old_id', '>=', 0)])
            for product_cat in product_cat_obj:
                product_cat.unlink()


            # Upload Data
            # =============
            list_of_parent = []
            for row_num in range(sheet.nrows):
                if row_num == 0:
                    continue
                list_of_parent.append(int(sheet.row(row_num)[3].value))

            list_of_parent.sort()
            # list_of_parent_lower = list_of_parent[0]
            # list_of_parent_upper = list_of_parent[-1]

            for row_num in range(sheet.nrows):
                if row_num == 0:
                    continue
                self.env['product.category'].create({'old_id': sheet.row(row_num)[0].value,
                                                     'name': sheet.row(row_num)[1].value,
                                                     'name_ar': sheet.row(row_num)[2].value,
                                                     'old_parent_id': sheet.row(row_num)[3].value,
                                                     'parent_id': product_cat_saleable_id,
                                                     'property_cost_method': 'fifo', })


            product_cat_list = self.env['product.category'].search([('old_parent_id', '>', 0)])

            for product_cat in product_cat_list:
                product_cat_obj = self.env['product.category'].search([('old_id', '=', product_cat.old_parent_id)], limit=1)
                product_cat_mod = self.env['product.category'].search([('id', '=', product_cat.id)],
                                                                      limit=1)
                product_cat_mod.write({'parent_id': product_cat_obj.id})

        except Exception as e:
            logger.exception("import_data Method")
            raise ValidationError(e)


