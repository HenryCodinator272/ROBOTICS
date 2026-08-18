from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import torch
import os
import torch.nn as nn
import time
from torchvision import transforms
from model import Bottle_Detection_Model
from torch.utils.data import TensorDataset, DataLoader, random_split
import visuals


def data_preparation():
    files = os.listdir('Training_Files')
    images = sorted(f for f in files if f.endswith('.jpg'))
    gt_tensors = sorted(f for f in files if f.endswith('.pt'))

    transform = transforms.Compose([transforms.Resize((224,224)),
                                    transforms.ToTensor(),
                                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std =[0.229, 0.224, 0.225])])

    label_tensors, image_tensors = [], []
    for image_file, gt_file in zip(images, gt_tensors):

        img = Image.open(os.path.join('Training_Files', image_file)).convert('RGB')
        img_tensor = transform(img)

        gt_label = torch.load(os.path.join('Training_Files', gt_file))

        image_tensors.append(img_tensor)
        label_tensors.append(gt_label)

    return label_tensors, image_tensors

def create_box(input_tensor, size = 224):
    new_tensor = input_tensor.detach().clone()
    new_tensor[:4] = new_tensor[:4] * size
    x_center, y_center, w, h, logit = new_tensor.detach().cpu().tolist()
    if logit >= 0.0: #we're not applying the sigmoid function to make a probability (I'm lazy) but prob is >0.5 when logit>0
        x1 = x_center - w/2
        x2 = x_center + w/2
        y1 = y_center - h/2
        y2 = y_center + h/2
        return [x1, x2, y1, y2, w, h]
    else:
        return None

def display_pred_box(pred, image_tensor):
    vals = create_box(pred[0])
    if vals:
        x1, x2, y1, y2, w, h = vals
    else:
        return

    def tensor_to_display(image):
        mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)

        image = image.cpu() * std + mean
        image = image.clamp(0, 1)

        return image.permute(1, 2, 0).numpy()

    array = tensor_to_display(image_tensor[0])
    fig, ax = plt.subplots()
    ax.imshow(array)
    box = Rectangle(
        (x1, y1),
        w,
        h,
        fill=False,
        linewidth=2,
        edgecolor = 'red'
    )

    ax.add_patch(box)
    ax.axis("off")
    os.makedirs('visuals', exist_ok=True)
    plt.savefig(os.path.join('visuals', 'test_result.jpg'))
    plt.close('all')


def main(epochs = 20, verbose = False):

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    generator = torch.Generator().manual_seed(42)
    labels, inputs = data_preparation()
    dataset = TensorDataset(torch.stack(inputs), torch.stack(labels))
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_set, val_set = random_split(dataset, [train_size, val_size], generator = generator)
    train_loader = DataLoader(train_set, shuffle = True, batch_size = 8)
    eval_loader = DataLoader(val_set, batch_size = 8)

    model = Bottle_Detection_Model().to(device)

    box_loss = nn.MSELoss()
    confidence_loss = nn.BCEWithLogitsLoss()

    for params in model.resnet.parameters():
        params.requires_grad = False
    for params in model.resnet.fc.parameters():
        params.requires_grad = True

    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    train_loss, evaluation_loss = [], []
    best_f1 = 0.0

    for i in range(epochs):
        print(f'Epoch {i+1}/{epochs}\n')
        total_loss = 0
        model.train()

        for image_tensor, gt_tensor in train_loader:
            image_tensor = image_tensor.to(device)
            gt_tensor = gt_tensor.to(device)
            has_bottle = gt_tensor[:, 4] == 1.0

            optimizer.zero_grad()
            pred = model(image_tensor)

            if has_bottle.any():
                b_loss = box_loss(
                    pred[has_bottle, :4],
                    gt_tensor[has_bottle, :4])
            else:
                b_loss = torch.tensor(0.0, device=device)

            c_loss = confidence_loss(pred[:, 4], gt_tensor[:, 4])
            loss = b_loss + c_loss
            total_loss += loss.item()
            loss.backward()
            optimizer.step()

        train_loss.append(total_loss/len(train_loader))

        model.eval()
        with torch.no_grad():
            eval_loss = 0.0
            pred_confidence, true_confidence = [], []
            for image_tensor, gt_tensor in eval_loader:

                image_tensor = image_tensor.to(device)
                gt_tensor = gt_tensor.to(device)
                pred = model(image_tensor)

                if verbose:
                    display_pred_box(pred, image_tensor) #visuals

                true_confidence.append(gt_tensor[:, 4].cpu())
                pred_confidence.append(torch.sigmoid(pred[:, 4]).cpu())
                c_loss = confidence_loss(pred[:, 4], gt_tensor[:, 4])
                has_bottle = gt_tensor[:, 4] == 1.0
                if has_bottle.any():
                    b_loss = box_loss(
                        pred[has_bottle, :4],
                        gt_tensor[has_bottle, :4])
                else:
                    b_loss = torch.tensor(0.0, device=device)
                loss = c_loss + b_loss
                eval_loss += loss.item()
        evaluation_loss.append(eval_loss/len(eval_loader))
        visuals.loss_graphs(evaluation_loss, train_loss)

        true_confidence = torch.cat(true_confidence)
        pred_confidence = torch.cat(pred_confidence)

        prediction = pred_confidence >= 0.5
        truth = true_confidence == 1.0

        tp, fp, tn, fn = 0, 0, 0, 0

        for n in range(len(prediction)):
            if prediction[n] and truth[n]:
                tp += 1
            elif prediction[n] and not truth[n]:
                fp += 1
            elif not prediction[n] and truth[n]:
                fn += 1
            elif not prediction[n] and not truth[n]:
                tn += 1

        recall = tp/(tp+fn) if tp + fn > 0 else 0.0
        precision = tp/(fp+tp) if fp + tp > 0 else 0.0
        f1_score = 2 * recall * precision / (recall + precision) if recall + precision > 0 else 0.0
        print(f'\nPrevious Best F1 Score: {best_f1:.03f}\n Current F1 Score: {f1_score:.03f}\n')

        if f1_score > best_f1:
            best_f1 = f1_score
            torch.save(model.state_dict(), 'best_bottle_model.pth')




if __name__ == '__main__':
    main()