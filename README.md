# Pré-processamento de EEG com MNE-Python
Ferramenta para pré-processamento de dados EEG do BrainVision Recorder (.vhdr, .eeg, .vmrk) usando MNE-Python.

## Introdução
Este projeto fornece ferramentas para o pré-processamento de sinais EEG gerados no software BrainVision Recorder. Utiliza a biblioteca MNE-Python para carregar, processar e visualizar dados EEG.

## Funcionalidades
- Carregamento de dados EEG em formato BrainVision (.vhdr, .eeg, .vmrk)
- Pré-processamento e limpeza de dados EEG
- Visualização de sinais EEG

## Instalação
Para instalar as dependências necessárias, execute:
```bash
pip install -r requirements.txt
```

## Uso
Para pré-processar e visualizar os dados EEG, execute o script principal:
```bash
python main.py
```

## Estrutura do Projeto
- `datasets/`: Contém os conjuntos de dados de EEG.
- `outputs_eeg/`: Armazena os dados EEG processados.
- `notebooks/`: Notebooks Jupyter complementar para pré-processamento e visualização.
- `src/`: Código-fonte do projeto.
- `main.py`: Script principal para pré-processamento e visualização.

## Requisitos
- `mne` 0.24.1
- `numpy` 1.21.2
- `matplotlib` 3.4.3
- `scipy` 1.7.1
- `pandas` 1.3.3

## Autor
- [@abner-lucas](https://github.com/abner-lucas)
  
## Licença
Este projeto está licenciado sob a licença MIT. Veja o arquivo [MIT](https://choosealicense.com/licenses/mit/) para mais detalhes
