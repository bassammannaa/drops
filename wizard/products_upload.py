# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
import xlrd
import tempfile
import base64

logger = logging.getLogger(__name__)


class ProductsUpload(models.TransientModel):
    _name = "drops.products.upload"
    _description = "Products Upload"

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
            if sheet.ncols != 8:
                raise ValidationError("Number of book Columns are less or more than 8 columns.")
            if sheet.nrows < 2:
                raise ValidationError("Number of book records are less or more than 1 row.")


            # Clear data
            # =============
            product_template_obj = self.env['product.template'].search([('old_id', '>=', 0)])
            for product_template in product_template_obj:
                product_template.unlink()

            # product_product_obj = self.env['product.product'].search([('old_id', '>=', 0)])
            # for product_product in product_product_obj:
            #     product_product.unlink()

            # Upload Data
            # =============
            for row_num in range(sheet.nrows):
                if row_num == 0:
                    continue

                # product_obj = self.env['product.product'].create({'old_id': sheet.row(row_num)[0].value,
                #                                 'default_code': sheet.row(row_num)[4].value, })



                category_obj = self.env['product.category'].search([('old_id', '=', sheet.row(row_num)[3].value)],
                                                                   limit = 1)

                self.env['product.template'].create({'old_id': sheet.row(row_num)[0].value,
                                                     'name': sheet.row(row_num)[1].value,
                                                     'name_ar': sheet.row(row_num)[2].value,
                                                     'categ_id': category_obj.id if category_obj else 4,
                                                     'default_code': sheet.row(row_num)[4].value,
                                                     'description': sheet.row(row_num)[5].value,
                                                     'list_price': sheet.row(row_num)[6].value,
                                                     'standard_price': sheet.row(row_num)[7].value,
                                                     'sale_ok': 'true',
                                                     'purchase_ok': 'true', })

        except Exception as e:
            logger.exception("import_data Method")
            raise ValidationError(e)


