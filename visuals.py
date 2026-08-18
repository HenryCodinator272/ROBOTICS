import matplotlib.pyplot as plt
import os

def loss_graphs(eval_loss, train_loss):
    fig, [ax1, ax2] = plt.subplots(1, 2, figsize = (9, 5))
    X = [i+1 for i in range(len(train_loss))]

    if len(X) == 1:
        ax1.scatter(X, eval_loss)
        ax2.scatter(X, train_loss)
    else:
        ax1.plot(X, eval_loss, marker = '.')
        ax2.plot(X, train_loss, marker = '.')
        ax1.fill_between(X, eval_loss, alpha=0.3)
        ax2.fill_between(X, train_loss, alpha=0.3)

    plt.suptitle(f'EVALUATION AND TRAINING LOSS')

    ax1.set_title(f'Evaluation Loss vs. Epoch')
    ax1.set_xlabel(f'Epoch')
    ax1.set_ylabel(f'Eval Loss')
    ax1.set_ylim(0, 1)
    ax1.grid()

    ax2.set_title(f'Train Loss vs. Epoch')
    ax2.set_xlabel(f'Epoch')
    ax2.set_ylabel(f'Train Loss')
    ax2.set_ylim(0, 1)
    ax2.grid()

    os.makedirs('Graphs', exist_ok = True)
    fig.savefig(os.path.join('Graphs', 'loss_graph.jpg'))
    plt.close('all')



if __name__ == '__main__':
    loss_graphs([0.8,0.6,0.5, 0.45, 0.43], [0.9, 0.5, 0.3, 0.2, 0.15])