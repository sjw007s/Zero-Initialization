import torch
import torchvision
import csv
import numpy as np
import torch.nn.functional as F
from torch import Tensor
from functools import partial
from typing import Any, Callable, List, Optional, Type, Union

from torch.utils.data import DataLoader
from torch.utils.data import TensorDataset
from torch import nn
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using {device} device")
#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print('Device:', device)
print('Current cuda device:', torch.cuda.current_device())
print('Count of using GPUs:', torch.cuda.device_count())
#print(torch.cuda.current_device())

local_adress = "temp"

temp_list = list()
r=open(local_adress+'/cifar-10-python/training_data_CIFAR.csv', 'r' )
reader=csv.reader(r)
for target in reader:
    temp_list.append(target)
training_data = np.array(temp_list).reshape((-1, 3, 32, 32)).astype(np.float32)
print(training_data.shape)
tt = torch.from_numpy(training_data).to("cuda")
training_data = torch.zeros((50000, 3, 40, 40)).to("cuda")
training_data[:,:,4:36,4:36] = tt
temp_list = list()
r=open(local_adress+'/cifar-10-python/test_data_CIFAR.csv', 'r' )
reader=csv.reader(r)
for target in reader:
    temp_list.append(target)
test_data = np.array(temp_list).reshape((-1, 3, 32, 32)).astype(np.float32)
print(test_data.shape)
test_data = torch.from_numpy(test_data).to("cuda")

temp_list = list()
r=open(local_adress+'/cifar-10-python/training_target_CIFAR.csv', 'r' )
reader=csv.reader(r)
for target in reader:
    if target[0] == '0':
        temp_list.append([1,0,0,0,0,0,0,0,0,0])
        continue
    if target[0] == '1':
        temp_list.append([0,1,0,0,0,0,0,0,0,0])
        continue
    if target[0] == '2':
        temp_list.append([0,0,1,0,0,0,0,0,0,0])
        continue
    if target[0] == '3':
        temp_list.append([0,0,0,1,0,0,0,0,0,0])
        continue
    if target[0] == '4':
        temp_list.append([0,0,0,0,1,0,0,0,0,0])
        continue
    if target[0] == '5':
        temp_list.append([0,0,0,0,0,1,0,0,0,0])
        continue
    if target[0] == '6':
        temp_list.append([0,0,0,0,0,0,1,0,0,0])
        continue
    if target[0] == '7':
        temp_list.append([0,0,0,0,0,0,0,1,0,0])
        continue
    if target[0] == '8':
        temp_list.append([0,0,0,0,0,0,0,0,1,0])
        continue
    if target[0] == '9':
        temp_list.append([0,0,0,0,0,0,0,0,0,1])
        continue 
training_target = np.array(temp_list).astype(np.float32)
print(training_target.shape)
training_target = torch.from_numpy(training_target).to("cuda")

temp_list = list()
r=open(local_adress+'/cifar-10-python/test_target_CIFAR.csv', 'r' )
reader=csv.reader(r)
for target in reader:
    if target[0] == '0':
        temp_list.append([1,0,0,0,0,0,0,0,0,0])
        continue
    if target[0] == '1':
        temp_list.append([0,1,0,0,0,0,0,0,0,0])
        continue
    if target[0] == '2':
        temp_list.append([0,0,1,0,0,0,0,0,0,0])
        continue
    if target[0] == '3':
        temp_list.append([0,0,0,1,0,0,0,0,0,0])
        continue
    if target[0] == '4':
        temp_list.append([0,0,0,0,1,0,0,0,0,0])
        continue
    if target[0] == '5':
        temp_list.append([0,0,0,0,0,1,0,0,0,0])
        continue
    if target[0] == '6':
        temp_list.append([0,0,0,0,0,0,1,0,0,0])
        continue
    if target[0] == '7':
        temp_list.append([0,0,0,0,0,0,0,1,0,0])
        continue
    if target[0] == '8':
        temp_list.append([0,0,0,0,0,0,0,0,1,0])
        continue
    if target[0] == '9':
        temp_list.append([0,0,0,0,0,0,0,0,0,1])
        continue 
test_target = np.array(temp_list).astype(np.float32)
print(test_target.shape)
test_target = torch.from_numpy(test_target).to("cuda")


batch_size = 100
epochs = 500

training_dataset = TensorDataset(training_data, training_target)
test_dataset = TensorDataset(test_data, test_target)

training_dataloader = DataLoader(training_dataset, batch_size=batch_size, shuffle=True)
test_dataloader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

def train(dataloader, model, loss_fn, optimizer):
    model.train()
    
    for batch, (X, y) in enumerate(dataloader):
        width_= torch.randint(0,8, (1,))
        height_= torch.randint(0,8, (1,))
        flip_=torch.randint(0,2,(1,))
        if flip_==0:
            with torch.autocast(device_type='cuda', dtype=torch.bfloat16):
                pred = model(X[:,:,height_:height_+32,width_:width_+32])
                batch_loss_result = loss_fn(pred, y)
        else:
            with torch.autocast(device_type='cuda', dtype=torch.bfloat16):
                pred = model(torch.flip(X[:,:,height_:height_+32,width_:width_+32],(3,)))
                batch_loss_result = loss_fn(pred, y)
        optimizer.zero_grad()
        batch_loss_result.backward()
        optimizer.step()
    
def test(dataloader, model, loss_fn):
    model.eval()
    with torch.no_grad():
        accuracy_sum=0
        
        for batch, (X, y) in enumerate(dataloader):
            with torch.autocast(device_type='cuda', dtype=torch.bfloat16):
                pred = model(X)
                batch_loss_result = loss_fn(pred, y)
            accuracy_sum+= (torch.argmax(pred, dim=1) == torch.argmax(y,dim=1)).type(torch.float).sum().item()
            
    return accuracy_sum/10000

def conv3x3(in_planes: int, out_planes: int, stride: int = 1, groups: int = 1, dilation: int = 1) -> nn.Conv2d:
    """3x3 convolution with padding"""
    return nn.Conv2d(
        in_planes,
        out_planes,
        kernel_size=3,
        stride=stride,
        padding=dilation,
        groups=groups,
        bias=False,
        dilation=dilation,
    )

def conv1x1(in_planes: int, out_planes: int, stride: int = 1) -> nn.Conv2d:
    """1x1 convolution"""
    return nn.Conv2d(in_planes, out_planes, kernel_size=1, stride=stride, bias=False)

class Bottleneck(nn.Module):
    # Bottleneck in torchvision places the stride for downsampling at 3x3 convolution(self.conv2)
    # while original implementation places the stride at the first 1x1 convolution(self.conv1)
    # according to "Deep residual learning for image recognition" https://arxiv.org/abs/1512.03385.
    # This variant is also known as ResNet V1.5 and improves accuracy according to
    # https://ngc.nvidia.com/catalog/model-scripts/nvidia:resnet_50_v1_5_for_pytorch.

    expansion: int = 4

    def __init__(
        self,
        inplanes: int,
        planes: int,
        stride: int = 1,
        downsample: Optional[nn.Module] = None,
        groups: int = 1,
        base_width: int = 64,
        dilation: int = 1,
        norm_layer: Optional[Callable[..., nn.Module]] = None,
    ) -> None:
        super().__init__()
        if norm_layer is None:
            norm_layer = nn.BatchNorm2d
        width = int(planes * (base_width / 64.0)) * groups
        # Both self.conv2 and self.downsample layers downsample the input when stride != 1
        self.conv1 = conv1x1(inplanes, width)
        self.bn1 = norm_layer(width)
        self.conv2 = conv3x3(width, width, stride, groups, dilation)
        self.bn2 = norm_layer(width)
        self.conv3 = conv1x1(width, planes * self.expansion)
        self.bn3 = norm_layer(planes * self.expansion)
        self.relu = nn.ReLU()
        self.downsample = downsample
        self.stride = stride
    def forward(self, x: Tensor) -> Tensor:
        identity = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        if self.downsample is not None:
            identity = self.downsample(x)
        #print("ㅎ")
        out += identity
        out = self.relu(out)

        return out

class ResNet(nn.Module):
    def __init__(
        self,
        block: Type[Bottleneck],
        layers: List[int],
        num_classes: int = 1000,
        zero_init_residual: bool = False,
        groups: int = 1,
        width_per_group: int = 64,
        replace_stride_with_dilation: Optional[List[bool]] = None,
        norm_layer: Optional[Callable[..., nn.Module]] = None,
    ) -> None:
        super().__init__()
      
        if norm_layer is None:
            norm_layer = nn.BatchNorm2d
        self._norm_layer = norm_layer

        self.inplanes = 64
        self.dilation = 1
        if replace_stride_with_dilation is None:
            # each element in the tuple indicates if we should replace
            # the 2x2 stride with a dilated convolution instead
            replace_stride_with_dilation = [False, False, False]
        if len(replace_stride_with_dilation) != 3:
            raise ValueError(
                "replace_stride_with_dilation should be None "
                f"or a 3-element tuple, got {replace_stride_with_dilation}"
            )
        self.groups = groups
        self.base_width = width_per_group
        self.conv1 = nn.Conv2d(3, self.inplanes, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn1 = norm_layer(self.inplanes)
        self.relu = nn.ReLU()
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.layer1 = self._make_layer(block, 64, layers[0])
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2, dilate=replace_stride_with_dilation[0])
        self.layer3 = self._make_layer(block, 256, layers[2], stride=2, dilate=replace_stride_with_dilation[1])
        self.layer4 = self._make_layer(block, 512, layers[3], stride=2, dilate=replace_stride_with_dilation[2])
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512 * block.expansion, num_classes)
        torch.nn.init.zeros_(self.fc.weight)
        torch.nn.init.zeros_(self.fc.bias)
        """
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode="fan_out", nonlinearity="relu")
            elif isinstance(m, (nn.BatchNorm2d, nn.GroupNorm)):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
        """
        # Zero-initialize the last BN in each residual branch,
        # so that the residual branch starts with zeros, and each residual block behaves like an identity.
        # This improves the model by 0.2~0.3% according to https://arxiv.org/abs/1706.02677
        if zero_init_residual:
            for m in self.modules():
                if isinstance(m, Bottleneck) and m.bn3.weight is not None:
                    nn.init.constant_(m.bn3.weight, 0)  # type: ignore[arg-type]
                elif isinstance(m, BasicBlock) and m.bn2.weight is not None:
                    nn.init.constant_(m.bn2.weight, 0)  # type: ignore[arg-type]

    def _make_layer(
        self,
        block: Type[Union[Bottleneck]],
        planes: int,
        blocks: int,
        stride: int = 1,
        dilate: bool = False,
    ) -> nn.Sequential:
        norm_layer = self._norm_layer
        downsample = None
        previous_dilation = self.dilation
        if dilate:
            self.dilation *= stride
            stride = 1
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                conv1x1(self.inplanes, planes * block.expansion, stride),
                norm_layer(planes * block.expansion),
            )

        layers = []
        layers.append(
            block(
                self.inplanes, planes, stride, downsample, self.groups, self.base_width, previous_dilation, norm_layer
            )
        )
        self.inplanes = planes * block.expansion
        for _ in range(1, blocks):
            layers.append(
                block(
                    self.inplanes,
                    planes,
                    groups=self.groups,
                    base_width=self.base_width,
                    dilation=self.dilation,
                    norm_layer=norm_layer,
                )
            )

        return nn.Sequential(*layers)

    def _forward_impl(self, x: Tensor) -> Tensor:
        # See note [TorchScript super()]
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        #print(x.shape)
        x = self.layer1(x)
        #print(x.shape)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        #print(x.shape)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)

        return x

    def forward(self, x: Tensor) -> Tensor:
        return self._forward_impl(x)


summary = list()
for i in range(10):
    model = ResNet(Bottleneck,[4,4,4,4],num_classes=10).to("cuda")
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.95)
    accuracy = 0 
    for t in range(epochs):
        #print(f"Epoch {t+1}\n-------------------------------")
        train(training_dataloader, model, loss_fn, optimizer)
        accuracy_temp = test(test_dataloader, model, loss_fn)
        scheduler.step()
        if accuracy_temp > accuracy:
            accuracy = accuracy_temp
    summary.append(accuracy)
    print(summary)
print("Done!")
