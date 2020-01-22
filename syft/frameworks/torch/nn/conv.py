import torch as th
from torch.nn import Module
<<<<<<< HEAD
import syft as sy
import sys
=======
>>>>>>> 49c56331cf6bca65c27da661d7e3b7635f4bc247


class Conv2d(Module):
    """
    This class is the beginning of an exact python port of the torch.nn.Conv2d
    module. Because PySyft cannot hook into layers which are implemented in C++,
    our special functionalities (such as encrypted computation) do not work with
    torch.nn.Conv2d and so we must have python ports available for all layer types
    which we seek to use.

    Note that this module has been tested to ensure that it outputs the exact output
    values that the main module outputs in the same order that the main module does.

    However, there is often some rounding error of unknown origin, usually less than
    1e-6 in magnitude.

    This module has not yet been tested with GPUs but should work out of the box.
    """

    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size,
        stride=(1, 1),
        padding=(0, 0),
        dilation=(1, 1),
        groups=1,
        bias=False,
        padding_mode="zeros",
        verbose=False,
    ):
        """For information on the constructor arguments, please see PyTorch's
        documentation in torch.nn.Conv2d"""

        super().__init__()

        # because my particular experiment does not demand full functionality of
        # a convolutional layer, I will only implement the basic functionality.
        # These assertions are the required settings.

        assert in_channels == 1
        assert stride == (1, 1)
        assert padding == (0, 0)
        assert dilation == (1, 1)
        assert groups == 1
        assert padding_mode == "zeros"

        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.dilation = dilation
        self.groups = groups
        self.has_bias = bias
        self.padding_mode = padding_mode

        self.verbose = verbose

        temp_init = th.nn.Conv2d(
            in_channels=self.in_channels,
            out_channels=self.out_channels,
            kernel_size=self.kernel_size,
            stride=self.stride,
            padding=self.padding,
            dilation=self.dilation,
            groups=self.groups,
            bias=self.has_bias,
            padding_mode=self.padding_mode,
        )

        self.weight = temp_init.weight
        self.bias = temp_init.bias

    def forward(self, data):

        batch_size, _, rows, cols = data.shape

        if self.verbose:
            sys.stdout.write("Conv - (Part 1/3) - 0%")

        expanded_data = data.unsqueeze(1).expand(batch_size, self.out_channels, 1, rows, cols)

        if self.verbose:
            sys.stdout.write("\rConv - (Part 1/3) - 50%")

        expanded_model = self.weight.unsqueeze(0).expand(
            batch_size, self.out_channels, 1, self.kernel_size[0], self.kernel_size[1]
        )

        if self.verbose:
            sys.stdout.write("\rConv - (Part 1/3) - 100%")

        kernel_results = list()

        for i in range(0, rows - self.kernel_size[0] + 1):

            if self.verbose:
                sys.stdout.write(
                    "\rConv - (Part 2/3) - "
                    + str((i / (rows - self.kernel_size[0] + 1)) * 100)[0:4]
                    + "%"
                )

            for j in range(0, cols - self.kernel_size[1] + 1):
                kernel_out = (
                    expanded_data[:, :, :, i : i + self.kernel_size[0], j : j + self.kernel_size[1]]
                    * expanded_model
                )
                kernel_out = kernel_out.sum((3, 4))s
                kernel_results.append(kernel_out)

        if self.verbose:
            sys.stdout.write("\rConv - (Part 3/3) - 0%")

        pred = th.cat(kernel_results, axis=2)

        if self.verbose:
            sys.stdout.write("\rConv - (Part 3/3) - 33%")

        pred = pred.view(
            batch_size,
            self.out_channels,
            rows - self.kernel_size[0] + 1,
            cols - self.kernel_size[1] + 1,
        )

        if self.verbose:
            sys.stdout.write("\rConv - (Part 3/3) - 66%")

        if self.has_bias:
            pred = pred + self.bias.unsqueeze(0).unsqueeze(2).unsqueeze(3).expand(
                batch_size,
                self.out_channels,
                rows - self.kernel_size[0] + 1,
                cols - self.kernel_size[1] + 1,
            )

        if self.verbose:
            sys.stdout.write("\rConv - (Part 3/3) - 100%")
            print("")

        return pred

    def __repr__(self):
        return str(self)

    def __str__(self):
        out = "Conv2d-Handcrafted("
        out += str(self.in_channels) + ", "
        out += str(self.out_channels) + ", "
        out += "kernel_size=" + str(self.kernel_size) + ", "
        out += "stride=" + str(self.stride)
        out += ")"
        return out

    def torchcraft(self):
        """Converts this handcrafted module into a torch.nn.Conv2d module wherein all the
        module's features are executing in C++. This will increase performance at the cost of
        some of PySyft's more advanced features such as encrypted computation."""

        kwargs = {}
        kwargs["in_channels"] = self.in_channels
        kwargs["out_channels"] = self.out_channels
        kwargs["kernel_size"] = self.kernel_size
        kwargs["stride"] = self.stride
        kwargs["padding"] = self.padding
        kwargs["dilation"] = self.dilation
        kwargs["groups"] = self.groups
        kwargs["bias"] = self.bias is not None
        kwargs["padding_mode"] = self.padding_mode

        model = th.nn.Conv2d(**kwargs)
        model.weight = self.weight
        model.bias = self.bias

        return model


def handcraft(self):
    """Converts a torch.nn.Conv2d module to a handcrafted one wherein all the
    module's features are executing in python. This is necessary for some of PySyft's
    more advanced features (like encrypted computation)."""

    kwargs = {}
    kwargs["in_channels"] = self.in_channels
    kwargs["out_channels"] = self.out_channels
    kwargs["kernel_size"] = self.kernel_size
    kwargs["stride"] = self.stride
    kwargs["padding"] = self.padding
    kwargs["dilation"] = self.dilation
    kwargs["groups"] = self.groups
    kwargs["bias"] = self.bias is not None
    kwargs["padding_mode"] = self.padding_mode
    kwargs["verbose"] = False

    model = sy.frameworks.torch.nn.Conv2d(**kwargs)
    model.weight = self.weight
    model.bias = self.bias

    return model


th.nn.Conv2d.handcraft = handcraft

