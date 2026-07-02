# Piped into `odoo shell` after install. Points the module at the mock API and
# sets a known admin password so Playwright can log in.
env = self.env  # noqa: F821 (provided by odoo shell)
params = env["ir.config_parameter"].sudo()
params.set_param("addressable_autocomplete.api_key", "test-key")
params.set_param("addressable_autocomplete.base_url", "http://mock:8000")
params.set_param("addressable_autocomplete.default_country", "nz")
env.ref("base.user_admin").password = "admin"
env.cr.commit()
print("SEED_OK")
