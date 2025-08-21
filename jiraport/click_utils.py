import click
import pendulum

class DateParamtype(click.ParamType):
    name = "date"

    def convert(self, value: str, param, ctx):
        try:
            return pendulum.from_format(value, "MM/DD/YYYY").date()
        except:
            self.fail(f"{value!r}. Example: '12/31/2025'", param, ctx)
